# coding=utf-8
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.

from abc import ABCMeta, abstractmethod
from math import log, floor

from google.protobuf.json_format import MessageToJson, Parse
from pyqrllib.pyqrllib import bin2hstr

from qbitcoin.core import config
from qbitcoin.core.State import State
from qbitcoin.core.OptimizedAddressState import OptimizedAddressState
from qbitcoin.core.StateContainer import StateContainer
from qbitcoin.core.misc import logger
from qbitcoin.core.txs import build_tx as main_build_tx
from qbitcoin.core.FalconHelper import falcon_pk_to_address
from qbitcoin.core.FalconHelper import falcon_pk_to_address, is_falcon_public_key
from qbitcoin.crypto.misc import sha256
from qbitcoin.crypto.falcon import FalconSignature
from qbitcoin.generated import qbit_pb2

CODEMAP = {
    'transfer': 1,
    'coinbase': 2,
    'latticePK': 3,
    'message': 4,
    'token': 5,
    'transfer_token': 6,
    'slave': 7,
    'multi_sig_create': 8,
    'multi_sig_spend': 9,
    'multi_sig_vote': 10,
}


class Transaction(object, metaclass=ABCMeta):
    """
    Abstract Base class to be derived by all other transactions
    """

    def __init__(self, protobuf_transaction=None):
        self._data = protobuf_transaction  # This object cointains persistable data
        if protobuf_transaction is None:
            self._data = qbit_pb2.Transaction()

    def __lt__(self, tx):
        if self.fee < tx.fee:
            return True
        return False

    def __gt__(self, tx):
        if self.fee > tx.fee:
            return True
        return False

    @property
    def size(self):
        return self._data.ByteSize()

    @property
    def pbdata(self):
        """
        Returns a protobuf object that contains persistable data representing this object
        :return: A protobuf Transaction object
        :rtype: qbit_pb2.Transaction
        """
        return self._data

    @property
    def type(self):
        return self._data.WhichOneof('transactionType')

    @property
    def fee(self):
        return self._data.fee

    @property
    def nonce(self):
        return self._data.nonce

    @property
    def master_addr(self):
        return self._data.master_addr

    @property
    def addr_from(self):
        if self.master_addr:
            return self.master_addr

        return falcon_pk_to_address(self.PK)

    @property
    def ots_key(self):
        # With Falcon, we don't have OTS keys
        # Instead, we identify transactions by their public key
        return None

    @staticmethod
    def calc_allowed_decimals(value):
        if not isinstance(value, int):
            raise ValueError('value should be of integer type')
        if value == 0:
            return 19

        # floor value could be negative, so return 0 when the floor value is negative
        return max(floor(19 - log(value, 10)), 0)

    @property
    def PK(self):
        return self._data.public_key

    @property
    def signature(self):
        return self._data.signature

    @staticmethod
    def from_pbdata(pbdata: qbit_pb2.Transaction):
        return main_build_tx(pbdata.WhichOneof('transactionType'), pbdata)

    @staticmethod
    def from_json(json_data):
        pbdata = qbit_pb2.Transaction()
        Parse(json_data, pbdata)
        return Transaction.from_pbdata(pbdata)

    @staticmethod
    def get_slave(tx):
        addr_from_pk = falcon_pk_to_address(tx.PK)
        if addr_from_pk != tx.addr_from:
            return addr_from_pk
        return None

    @property
    def txhash(self) -> bytes:
        return self._data.transaction_hash

    def update_txhash(self):
        self._data.transaction_hash = self.generate_txhash()

    def generate_txhash(self):
        return sha256(
            self.get_data_hash() +
            self.signature +
            self.PK
        )

    def get_data_bytes(self) -> bytes:
        """
        This method returns the essential bytes that represent the transaction and will be later signed
        :return:
        """
        raise NotImplementedError

    def get_data_hash(self) -> bytes:
        """
        This method returns the hashes of the transaction data.
        :return:
        """
        return sha256(self.get_data_bytes())

    def sign(self, object_with_sign_method):
        self._data.signature = object_with_sign_method.sign(self.get_data_hash())
        self.update_txhash()

    def set_affected_address(self, addresses_set: set):
        addresses_set.add(self.addr_from)
        addresses_set.add(falcon_pk_to_address(self.PK))

    @abstractmethod
    def _validate_custom(self) -> bool:
        """
        This is an extension point for derived classes validation
        If derived classes need additional field validation they should override this member
        """
        raise NotImplementedError

    @abstractmethod
    def _validate_extended(self, state_container: StateContainer) -> bool:
        raise NotImplementedError

    @abstractmethod
    def apply(self,
              state: State,
              state_container: StateContainer) -> bool:
        raise NotImplementedError

    @abstractmethod
    def revert(self,
               state: State,
               state_container: StateContainer) -> bool:
        raise NotImplementedError

    def validate_transaction_pool(self, transaction_pool):
        for tx_set in transaction_pool:
            txn = tx_set[1].transaction
            if txn.txhash == self.txhash:
                continue

            if self.PK != txn.PK:
                continue

            # Falcon public key reuse validation removed - allowing multiple transactions with same public key

        return True

    def validate(self, verify_signature=True) -> bool:
        """
        This method calls validate_or_raise, logs any failure and returns True or False accordingly
        The main purpose is to avoid exceptions and accommodate legacy code
        :return: True is the transaction is valid
        :rtype: bool
        """
        try:
            self.validate_or_raise(verify_signature)
        except ValueError as e:
            logger.info('[%s] failed validate_tx', bin2hstr(self.txhash))
            logger.warning(str(e))
            return False
        except Exception as e:
            logger.exception(e)
            return False
        return True

    def validate_all(self, state_container: StateContainer, check_nonce=True) -> bool:
        # Check banned addresses only after hard fork height (index 0 = banned address enforcement)
        current_block_number = state_container.block_number
        banned_address_hard_fork_height = state_container.current_dev_config.hard_fork_heights[0]
        
        if current_block_number >= banned_address_hard_fork_height:
            for banned_address in state_container.current_dev_config.banned_address:
                tx_type = self.pbdata.WhichOneof('transactionType')
                addr_from_pk = None
                if tx_type != 'coinbase':
                    addr_from_pk = falcon_pk_to_address(self.PK)

                if addr_from_pk == banned_address or self.master_addr == banned_address:
                    logger.warning(f"Banned Qbitcoin Address found in master_addr or pk at block {current_block_number} (banned since block {banned_address_hard_fork_height})")
                    return False
                if tx_type == 'coinbase':
                    if self.pbdata.coinbase.addr_to == banned_address:
                        logger.warning(f"Banned Qbitcoin Address found in coinbase.addr_to at block {current_block_number}")
                        return False
                elif tx_type == 'message':
                    if self.pbdata.message.addr_to == banned_address:
                        logger.warning(f"Banned Qbitcoin Address found in message.addr_to at block {current_block_number}")
                        return False
                elif tx_type == 'transfer':
                    for addr_to in self.pbdata.transfer.addrs_to:
                        if banned_address == addr_to:
                            logger.warning(f"Banned Qbitcoin Address found in transfer.addr_to at block {current_block_number}")
                            return False
                elif tx_type == 'token':
                    # Token transactions don't have recipient addresses to check
                    # Only sender validation (already done above with addr_from_pk)
                    pass
                elif tx_type == 'transfer_token':
                    for addr_to in self.pbdata.transfer_token.addrs_to:
                        if banned_address == addr_to:
                            logger.warning(f"Banned Qbitcoin Address found in transfer_token.addr_to at block {current_block_number}")
                            return False
                elif tx_type == 'slave':
                    for slave_pk in self.pbdata.slave.slave_pks:
                        slave_addr = falcon_pk_to_address(slave_pk)
                        if banned_address == slave_addr:
                            logger.warning(f"Banned Qbitcoin Address found in slave addresses at block {current_block_number}")
                            return False
                elif tx_type == 'latticePK':
                    # Lattice transactions don't have recipient addresses
                    # Only sender validation (already done above with addr_from_pk)
                    pass
                elif tx_type == 'multi_sig_create':
                    # Check all signatories in multi-sig creation
                    for signatory in self.pbdata.multi_sig_create.signatories:
                        if banned_address == signatory:
                            logger.warning(f"Banned Qbitcoin Address found in multi_sig_create.signatories at block {current_block_number}")
                            return False
                elif tx_type == 'multi_sig_spend':
                    # Check all addresses to in multi-sig spend
                    for addr_to in self.pbdata.multi_sig_spend.addrs_to:
                        if banned_address == addr_to:
                            logger.warning(f"Banned Qbitcoin Address found in multi_sig_spend.addr_to at block {current_block_number}")
                            return False
                elif tx_type == 'multi_sig_vote':
                    # Multi-sig vote transactions don't have recipient addresses
                    # Only sender validation (already done above with addr_from_pk)
                    pass

        if self.pbdata.WhichOneof('transactionType') == 'coinbase':
            if not self._validate_extended(state_container):
                return False
            return True

        if not self.validate(True):  # It also calls _validate_custom
            return False
        if not self.validate_slave(state_container):
            return False
        if not self._validate_extended(state_container):
            return False

        addr_from_pk = falcon_pk_to_address(self.PK)
        addr_from_pk_state = state_container.addresses_state[addr_from_pk]

        expected_nonce = addr_from_pk_state.nonce + 1

        if check_nonce and self.nonce != expected_nonce:
            logger.warning('nonce incorrect, invalid tx')
            logger.warning('subtype: %s', self.type)
            logger.warning('%s actual: %s expected: %s',
                           OptimizedAddressState.bin_to_qaddress(addr_from_pk),
                           self.nonce,
                           expected_nonce)
            return False

        # Falcon public key reuse validation removed - allowing multiple transactions with same public key

        return True

    # TODO: will need state_container
    def _coinbase_filter(self):
        if config.dev.coinbase_address in [falcon_pk_to_address(self.PK), self.master_addr]:
            raise ValueError('Coinbase Address only allowed to do Coinbase Transaction')

    def _get_allowed_access_types(self):
        return [0]

    def _get_master_address(self):
        return self.addr_from

    # TODO: will need state_container
    def validate_or_raise(self, verify_signature=True) -> bool:
        """
        This method will validate a transaction and raise exception if problems are found
        :return: True if the exception is valid, exceptions otherwise
        :rtype: bool
        """
        if not self._validate_custom():
            raise ValueError("Custom validation failed")

        self._coinbase_filter()

        expected_transaction_hash = self.generate_txhash()
        if verify_signature and self.txhash != expected_transaction_hash:
            logger.warning('Invalid Transaction hash')
            logger.warning('Expected Transaction hash %s', bin2hstr(expected_transaction_hash))
            logger.warning('Found Transaction hash %s', bin2hstr(self.txhash))
            raise ValueError("Invalid Transaction Hash")

        if verify_signature:
            # Use Falcon512 for signature verification
            if not FalconSignature.verify_signature(self.get_data_hash(),
                                                    self.signature,
                                                    self.PK):
                raise ValueError("Invalid Falcon512 signature")

        return True

    def validate_slave(self, state_container: StateContainer) -> bool:
        addr_from_pk = falcon_pk_to_address(self.PK)

        master_address = self._get_master_address()
        allowed_access_types = self._get_allowed_access_types()

        # If master_addr is not set or equals addr_from_pk, this is a normal transaction
        if not self.master_addr or self.master_addr == addr_from_pk:
            return True

        # This is a slave transaction - master_addr is set and different from addr_from_pk
        if addr_from_pk != master_address:
            if (self.addr_from, self.PK) not in state_container.slaves.data:
                logger.warning("Public key and address doesn't match")
                return False

            slave_access_type = state_container.slaves.data[(self.addr_from, self.PK)].access_type
            if slave_access_type not in allowed_access_types:
                logger.warning('Access Type %s', slave_access_type)
                logger.warning('Slave Address doesnt have sufficient permission')
                return False

        return True

    def get_message_hash(self):
        # FIXME: refactor, review that things are not recalculated too often, cache, etc.
        return self.txhash

    def to_json(self):
        # FIXME: Remove once we move completely to protobuf
        return MessageToJson(self._data, sort_keys=True)

    def serialize(self) -> str:
        return self._data.SerializeToString()

    @staticmethod
    def deserialize(data):
        pbdata = qbit_pb2.Transaction()
        pbdata.ParseFromString(bytes(data))
        tx = Transaction(pbdata)
        return tx

    def _apply_state_changes_for_PK(self,
                                    state_container: StateContainer) -> bool:
        addr_from_pk = falcon_pk_to_address(self.PK)
        address_state = state_container.addresses_state[addr_from_pk]
        if self.addr_from != addr_from_pk:
            state_container.paginated_tx_hash.insert(address_state, self.txhash)
        address_state.increase_nonce()
        # Track the Falcon public key instead of OTS key
        state_container.paginated_bitfield.set_ots_key(state_container.addresses_state, addr_from_pk, self.PK)

        return True

    def _revert_state_changes_for_PK(self,
                                     state_container: StateContainer) -> bool:
        addr_from_pk = falcon_pk_to_address(self.PK)
        address_state = state_container.addresses_state[addr_from_pk]
        if self.addr_from != addr_from_pk:
            state_container.paginated_tx_hash.remove(address_state, self.txhash)
        address_state.decrease_nonce()
        # Remove the Falcon public key instead of OTS key
        state_container.paginated_bitfield.unset_ots_key(state_container.addresses_state, addr_from_pk, self.PK)

        return True
