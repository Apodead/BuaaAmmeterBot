import telegram
import telegram.ext
import crawler
import db as iddb
import configure as conf
from pydblite import Base
import logging
import datetime

pp = telegram.utils.request.Request(read_timeout=20)
bot = telegram.Bot(token=conf.bot_token, request=pp, base_url=conf.base_url)

updater = telegram.ext.Updater(bot=bot, use_context=True)

log = logging.RootLogger(level = logging.DEBUG)
logging.basicConfig(level = logging.INFO)

db = Base('bind.pdl')
if not db.exists():
    db.create('tg_user_id', 'meter_id')
else:
    db.open()

def handle_bind_event(update, context):
    log.info("Handle bind event.")
    uid = update.effective_user.id
    mids = ""
    for mid in context.args:
        if [i for i in ((db('tg_user_id')==uid)&(db('meter_id')==mid))]==[]:
            db.insert(uid,mid)
            mids += '<pre>' + str(mid) + '<\pre>\n'
            log.info("Insert new bind record:{} - {}".format(uid,mid))
    db.commit()
    if mids == "":
        bot.sendMessage(update.effective_chat.id, "没有绑定新的电表。".format(mids), parse_mode="HTML")
    else:
        bot.sendMessage(update.effective_chat.id, "已绑定以下购电表号：\n{}使用 /list 查看所有已绑定的电表。".format(mids), parse_mode="HTML")
    return
def handle_unbind_event(update, context):
    log.info("Handle bind event.")
    uid = update.effective_user.id
    mids = ""
    if context.args == None:
        db.delete(db('tg_user_id')==uid)
    else:
        for i in ((db('tg_user_id')==uid)&(db('meter_id')==context.args)):
            mids += '<pre>' + i['meter_id'] + '</pre>\n'
        db.delete((db('tg_user_id')==uid)&(db('meter_id')==context.args))
        db.commit()
    if mids == "" :
        bot.sendMessage(update.effective_chat.id, "没有找到记录。")
    else:
        bot.sendMessage(update.effective_chat.id, "已解除下列购电表号的绑定：\n{}使用 /list 查看所有已绑定的电表。".format(mids), parse_mode="HTML")

def handle_list_event(update, context):
    logging.info("Handle /list command.")
    uid = update.effective_user.id
    mids = ""
    for record in (db('tg_user_id')==uid):
        mids += '<pre>' + str(record['meter_id']) + '</pre>: '
        try:
            meter_name = iddb.queryMeterInfo(record['meter_id'])[3] # 4th item is ADDRESS
        except:
            meter_name = "未知电表"
        mids += meter_name + '\n'
    if mids == "" :
        bot.sendMessage(update.effective_chat.id, "没有找到记录。")
    else:
        bot.sendMessage(update.effective_chat.id, "已绑定的购电表号：\n{}".format(mids), parse_mode="HTML")

def generate_query_result(mid):
    try:
        rem,yst,his,tpu=crawler.query_usage(mid)
        meter_name = iddb.queryMeterInfo(mid)[3] # 4th item is ADDRESS
        text = "<b>{}</b>[{}]：\n昨日用电 <b>{}</b> kWh\t剩余电量 <b>{}</b> kWh\n".format \
                (meter_name, mid, yst, rem)
    except Exception as ex:
        logging.error("{}:{}".format(type(ex).__name__,str(ex)))
        text = "电表[{0}]查询失败，请重试或检查购电表号。发送 <pre>/unbind {0}</pre> 解绑此电表。\n".format(mid)
    return text
    
def handle_query_event(update, context):
    logging.info("Handle /query command.")
    uid = update.effective_user.id
    chat_id = update.effective_chat.id
    msgid = None
    msg_text = ""
    refresh_mids = ""
    def updateMsg(text, **kw):
        nonlocal msgid
        if msgid == None:
            msgid = bot.sendMessage(chat_id=chat_id, text=text, parse_mode="HTML").message_id
        else:
            bot.editMessageText(chat_id=chat_id, message_id=msgid, text=text, parse_mode="HTML")
    for i in ((db('tg_user_id')==uid)):
        msg_text += generate_query_result(i['meter_id'])
        logging.debug("Updating message text:"+msg_text)
        updateMsg(msg_text)
        refresh_mids += ':' + str(i['meter_id'])
    keyboard = [[telegram.InlineKeyboardButton("刷新",callback_data="refresh"+refresh_mids)]]
    reply_markup = telegram.InlineKeyboardMarkup(keyboard)
    bot.edit_message_reply_markup(chat_id=chat_id, message_id=msgid, reply_markup=reply_markup)

def handle_callback_data(update, context):
    data = update.callback_query.data
    if "refresh" in data:
        mids=data.split(':')[1:]
        logging.info("Handle refresh requests.")
        uid = update.effective_user.id
        chat_id = update.effective_chat.id
        msgid = update.callback_query.message.message_id
        msg_text = ""
        def updateMsg(text, **kw):
            nonlocal msgid
            if msgid == None:
                msgid = bot.sendMessage(chat_id=chat_id, text=text, parse_mode="HTML").message_id
            else:
                bot.editMessageText(chat_id=chat_id, message_id=msgid, text=text, parse_mode="HTML")
        bot.edit_message_reply_markup(chat_id=chat_id, message_id=msgid, reply_markup=None)
        updateMsg("正在刷新...")
        for mid in mids:
            msg_text += generate_query_result(mid)
            logging.debug("Updating message text:"+msg_text)
            updateMsg(msg_text)
        keyboard = [[telegram.InlineKeyboardButton("刷新",callback_data=data)]]
        reply_markup = telegram.InlineKeyboardMarkup(keyboard)
        bot.edit_message_reply_markup(chat_id=chat_id, message_id=msgid, reply_markup=reply_markup)
def handle_help_event(update, context):
    help_msg="欢迎使用 BuaaAmmter 电表查询 bot 。本 bot 目前仅提供绑定并查询电表余额的功能。\n\n"\
             "使用方法：请内网登录 http://shsd.buaa.edu.cn 查询您的购电表号，并使用 /bind 命令绑定"\
             "至您的帐号。您可以使用 /query 查询您绑定的所有电表的余额信息。\n\n"\
             "命令列表：\n/bind AmmeterId ... 绑定一个或者多个电表。\n/unbind AmmeterId ... 解除"\
             "一个或者多个电表的绑定；若不指定购电表号，则将解绑所有电表。\n/list 显示已绑定的电表"\
             "\n/query 查询所有已绑定电表"
def handle_start_event(update, context):
    handle_help_event(update, context)


updater.dispatcher.add_handler(telegram.ext.CommandHandler("start", handle_start_event))
updater.dispatcher.add_handler(telegram.ext.CommandHandler("help", handle_help_event))
updater.dispatcher.add_handler(telegram.ext.CommandHandler("bind", handle_bind_event))
updater.dispatcher.add_handler(telegram.ext.CommandHandler("unbind", handle_unbind_event))
updater.dispatcher.add_handler(telegram.ext.CommandHandler("list", handle_list_event))
updater.dispatcher.add_handler(telegram.ext.CommandHandler("query", handle_query_event))
updater.dispatcher.add_handler(telegram.ext.CallbackQueryHandler(handle_callback_data))
#updater.dispatcher.add_handler(telegram.ext.CallbackQueryHandler(handle_callback_data))
def start_bot():
    updater.start_polling()
    logging.warning("Start at {}".format(datetime.datetime.today().ctime()))
    updater.idle()
if __name__ == "__main__":
    start_bot()
