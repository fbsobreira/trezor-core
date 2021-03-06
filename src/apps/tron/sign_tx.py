from trezor import wire
from trezor.crypto.curve import secp256k1
from trezor.crypto.hashlib import sha256
from trezor.messages.TronSignedTx import TronSignedTx
from trezor.messages.TronSignTx import TronSignTx
from trezor.wire import ProcessError

from . import layout
from .helpers import _b58b, get_address_from_public_key
from .serialize import serialize

from apps.common import seed


async def sign_tx(ctx, msg: TronSignTx):
    """Parse and sign TRX transaction"""

    validate(msg)
    address_n = msg.address_n or ()
    node = await seed.derive_node(ctx, address_n)
    seckey = node.private_key()
    public_key = secp256k1.publickey(seckey, False)
    address = get_address_from_public_key(public_key[:65])

    try:
        await _require_confirm_by_type(ctx, msg, address)
    except AttributeError:
        raise wire.DataError("The transaction has invalid asset data field")

    raw_data = serialize(msg, address)
    data_hash = sha256(raw_data).digest()

    signature = secp256k1.sign(seckey, data_hash, False)

    signature = signature[1:65] + bytes([~signature[0] & 0x01])
    return TronSignedTx(signature=signature, serialized_tx=raw_data)


async def _require_confirm_by_type(ctx, transaction, owner_address):
    """Confirm extra data if exist"""
    if transaction.data:
        await layout.require_confirm_data(ctx, transaction.data)

    """Confirm transaction"""
    contract = transaction.contract
    if contract.transfer_contract:
        return await layout.require_confirm_tx(
            ctx,
            _b58b(contract.transfer_contract.to_address),
            contract.transfer_contract.amount,
        )

    if contract.transfer_asset_contract:
        return await layout.require_confirm_tx_asset(
            ctx,
            contract.transfer_asset_contract.asset_name,
            _b58b(contract.transfer_asset_contract.to_address),
            contract.transfer_asset_contract.amount,
        )

    if contract.vote_witness_contract:
        # count votes
        votes_addr = 0
        votes_total = 0
        for i in range(len(contract.vote_witness_contract.votes)):
            votes_addr += 1
            votes_total += contract.vote_witness_contract.votes[i].vote_count
        return await layout.require_confirm_vote_witness(ctx, votes_addr, votes_total)

    if contract.witness_create_contract:
        return await layout.require_confirm_witness_contract(
            ctx, contract.witness_create_contract.url
        )

    if contract.asset_issue_contract:
        return await layout.require_confirm_asset_issue(
            ctx,
            contract.asset_issue_contract.name,
            contract.asset_issue_contract.abbr,
            contract.asset_issue_contract.total_supply,
            contract.asset_issue_contract.trx_num,
            contract.asset_issue_contract.num,
        )

    if contract.witness_update_contract:
        return await layout.require_confirm_witness_update(
            ctx,
            str(owner_address, "utf-8"),
            contract.witness_update_contract.update_url,
        )

    if contract.participate_asset_issue_contract:
        return await layout.require_confirm_participate_asset(
            ctx,
            contract.participate_asset_issue_contract.asset_name,
            contract.participate_asset_issue_contract.amount,
        )

    if contract.account_update_contract:
        return await layout.require_confirm_account_update(
            ctx, contract.account_update_contract.account_name
        )

    if contract.freeze_balance_contract:
        return await layout.require_confirm_freeze_balance(
            ctx,
            contract.freeze_balance_contract.frozen_balance,
            contract.freeze_balance_contract.frozen_duration,
        )

    if contract.unfreeze_balance_contract:
        return await layout.require_confirm_unfreeze_balance(ctx)

    if contract.withdraw_balance_contract:
        return await layout.require_confirm_withdraw_balance(ctx)

    if contract.unfreeze_asset_contract:
        return await layout.require_confirm_unfreeze_asset(ctx)

    if contract.update_asset_contract:
        return await layout.require_confirm_update_asset(
            ctx,
            contract.update_asset_contract.description,
            contract.update_asset_contract.url,
        )

    if contract.proposal_create_contract:
        return await layout.require_confirm_proposal_create_contract(
            ctx, contract.proposal_create_contract.parameters
        )

    if contract.proposal_approve_contract:
        return await layout.require_confirm_proposal_approve_contract(
            ctx,
            contract.proposal_approve_contract.proposal_id,
            contract.proposal_approve_contract.is_add_approval,
        )

    if contract.proposal_delete_contract:
        return await layout.require_confirm_proposal_delete_contract(
            ctx, contract.proposal_delete_contract.proposal_id
        )

    raise wire.DataError("Invalid transaction type")


def validate(msg: TronSignTx):
    print(msg)
    if None in (msg.contract,):
        raise ProcessError(
            "Some of the required fields are missing (fee, sequence, payment.amount, payment.destination)"
        )
