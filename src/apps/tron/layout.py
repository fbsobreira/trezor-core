from trezor import ui
from trezor.messages import ButtonRequestType
from trezor.ui.text import Text
from trezor.utils import chunks

from apps.common.confirm import require_confirm


async def require_confirm_data(ctx, data):
    text = Text("Data attached", ui.ICON_CONFIRM, icon_color=ui.GREEN)
    text.normal(*split_text(data))
    return await require_confirm(ctx, text, ButtonRequestType.ConfirmOutput)


async def require_confirm_tx(ctx, dest, value):
    text = Text("Confirm sending", ui.ICON_SEND, icon_color=ui.GREEN)
    text.bold(format_amount_trx(value))
    text.mono(*split_address("To: " + dest))
    return await require_confirm(ctx, text, ButtonRequestType.SignTx)


async def require_confirm_tx_asset(ctx, token, dest, value):
    text = Text("Confirm sending", ui.ICON_SEND, icon_color=ui.GREEN)
    text.bold(format_amount_token(value) + token)
    text.mono(*split_address("To: " + dest))
    return await require_confirm(ctx, text, ButtonRequestType.SignTx)


async def require_confirm_vote_witness(ctx, votes_addr, votes_total):
    text = Text("Confirm transaction", ui.ICON_SEND, icon_color=ui.GREEN)
    text.bold("SR Voting")
    text.normal("N. Candidates: {}".format(votes_addr))
    text.normal("Total Votes: {}".format(votes_total))
    return await require_confirm(ctx, text, ButtonRequestType.SignTx)


async def require_confirm_witness_contract(ctx, url):
    text = Text("Confirm transaction", ui.ICON_SEND, icon_color=ui.GREEN)
    text.bold("Apply for SR")
    text.mono(*split_text("URL: {}".format(url)))
    return await require_confirm(ctx, text, ButtonRequestType.SignTx)


async def require_confirm_asset_issue(
    ctx, token_name, token_abbr, supply, trx_num, num
):
    text = Text("Confirm transaction", ui.ICON_SEND, icon_color=ui.GREEN)
    text.bold("Create Token")
    text.normal(token_name)
    text.normal("{} {}".format(supply, token_abbr))
    text.mono("Ratio {}:{}".format(trx_num, num))
    return await require_confirm(ctx, text, ButtonRequestType.SignTx)


async def require_confirm_witness_update(ctx, owner_address, update_url):
    text = Text("Confirm transaction", ui.ICON_SEND, icon_color=ui.GREEN)
    text.bold("Update Witness")
    text.normal(owner_address)
    text.mono(*split_address("URL: {}".format(update_url)))
    return await require_confirm(ctx, text, ButtonRequestType.SignTx)


async def require_confirm_participate_asset(ctx, token, value):
    text = Text("Confirm transaction", ui.ICON_SEND, icon_color=ui.GREEN)
    text.bold("Token Participate:")
    text.mono(token)
    text.bold("Amount:")
    text.mono(format_amount_token(value))
    return await require_confirm(ctx, text, ButtonRequestType.SignTx)


async def require_confirm_account_update(ctx, account_name):
    text = Text("Confirm transaction", ui.ICON_SEND, icon_color=ui.GREEN)
    text.bold("Account Update")
    text.mono("Name:")
    text.mono(account_name)
    return await require_confirm(ctx, text, ButtonRequestType.SignTx)


async def require_confirm_freeze_balance(ctx, value, days):
    text = Text("Confirm transaction", ui.ICON_SEND, icon_color=ui.GREEN)
    text.bold("Freeze Balance")
    text.mono("Amount:")
    text.bold(format_amount_trx(value))
    text.mono("Days: {}".format(days))
    return await require_confirm(ctx, text, ButtonRequestType.SignTx)


async def require_confirm_unfreeze_balance(ctx):
    text = Text("Confirm transaction", ui.ICON_SEND, icon_color=ui.GREEN)
    text.bold("Unfreeze Balance")
    text.mono(*split_text("Total frozen balance will be unfreeze."))
    return await require_confirm(ctx, text, ButtonRequestType.SignTx)


async def require_confirm_withdraw_balance(ctx):
    text = Text("Confirm transaction", ui.ICON_SEND, icon_color=ui.GREEN)
    text.bold("Withdraw Balance")
    text.mono(*split_text("Total allowance withdraw to your account."))
    return await require_confirm(ctx, text, ButtonRequestType.SignTx)


async def require_confirm_unfreeze_asset(ctx):
    text = Text("Confirm transaction", ui.ICON_SEND, icon_color=ui.GREEN)
    text.bold("Unfreeze Assets")
    text.mono(*split_text("Unfreeze expired frozen assets."))
    return await require_confirm(ctx, text, ButtonRequestType.SignTx)


async def require_confirm_update_asset(ctx, description, url):
    text = Text("Confirm transaction", ui.ICON_CONFIRM, icon_color=ui.GREEN)
    text.bold("Update Token")
    text.mono(*split_text(description))
    text.mono(url)
    return await require_confirm(ctx, text, ButtonRequestType.SignTx)


async def require_confirm_proposal_create_contract(ctx, parameters):
    for idx in range(len(parameters)):
        text = Text("Confirm proposal", ui.ICON_CONFIRM, icon_color=ui.GREEN)
        lines = "Parameter: {}".format(get_parameter_text(parameters[idx].key))
        text.normal(*split_text(lines))
        lines = "Value: {}".format(parameters[idx].value)
        text.mono(*split_text(lines))
        try:
            await require_confirm(ctx, text, ButtonRequestType.SignTx)
        except AttributeError:
            return False
    return True


async def require_confirm_proposal_approve_contract(ctx, proposal_id, is_add_approval):
    text = Text("Confirm transaction", ui.ICON_CONFIRM, icon_color=ui.GREEN)
    text.bold("Proposal Approval")
    text.mono("ID: {}".format(proposal_id))
    text.mono("Approve: {}".format(is_add_approval))
    return await require_confirm(ctx, text, ButtonRequestType.SignTx)


async def require_confirm_proposal_delete_contract(ctx, proposal_id):
    text = Text("Confirm transaction", ui.ICON_CONFIRM, icon_color=ui.GREEN)
    text.bold("Proposal Delete")
    text.mono("ID: {}".format(proposal_id))
    return await require_confirm(ctx, text, ButtonRequestType.SignTx)


def format_amount_trx(value):
    return "%s TRX" % (int(value) / 1000000)


def format_amount_token(value):
    return "%s " % int(value)


def split_address(address):
    return chunks(address, 16)


def split_text(text):
    return chunks(text, 18)


def get_parameter_text(code):
    parameter = {
        0: "Maintenance time interval",
        1: "Account upgrade cost",
        2: "Create account fee",
        3: "Transaction fee",
        4: "Asset issue fee",
        5: "Witness pay per block",
        6: "Witness standby allowance",
        7: "Create new account fee in system contract",
        8: "Create new account bandwidth rate",
        9: "Allow creation of contracts",
        10: "Remove the power of GRs",
        11: "Energy fee",
        12: "Exchange create fee",
        13: "Max CPU time of one TX",
    }
    return parameter.get(code, "Invalid parameter")
