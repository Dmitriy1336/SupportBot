from database.models import async_session
from database.models import User, Category, Item, Messages, Blacklist, Admin, Lead, Mettings_Info
from sqlalchemy import select, delete, update
from sqlalchemy import desc

async def set_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()

async def set_messages(tg_id, username, message, category, msg_id):
    async with async_session() as session:
        await session.scalar(select(Messages).where(Messages.tg_id == tg_id))
        await session.scalar(select(Messages).where(Messages.username == username))
        await session.scalar(select(Messages).where(Messages.message == message))
        await session.scalar(select(Messages).where(Messages.category == category))
        await session.scalar(select(Messages).where(Messages.msg_id == msg_id))
        session.add(Messages(tg_id=tg_id, username=username, message=message, category=category, msg_id=msg_id))
        await session.commit()

async def get_messages(message):
    async with async_session() as session:
        return await session.scalar(select(Messages.message).where(Messages.message == message))

async def get_messages_reply(message):
    async with async_session() as session:
        return await session.scalar(select(Messages.msg_id).where(Messages.message == message))


async def get_categories():
    async with async_session() as session:
        return await session.scalars(select(Category))

async def get_admins_info():
    async with async_session() as session:
        return await session.scalars(select(Admin))

async def get_admins_state(tg_id):
    async with async_session() as session:
        return await session.scalar(select(Admin).where(Admin.tg_id == tg_id))

async def get_category_item(category_id, from_admin):
    async with async_session() as session:
        return await session.scalar(select(Item).where(Item.category == category_id, Item.from_admin == from_admin))

async def get_item(item_id):
    async with async_session() as session:
        return await session.scalar(select(Item).where(Item.category == item_id))

async def give_ban(tg_id, reason, datetime):
    async with async_session() as session:
        await session.scalar(select(Blacklist).where(Blacklist.tg_id == tg_id))
        await session.scalar(select(Blacklist).where(Blacklist.reason == reason))
        await session.scalar(select(Blacklist).where(Blacklist.datetime == datetime))
        session.add(Blacklist(tg_id=tg_id, reason=reason, datetime=datetime))
        await session.commit()
async def get_banned_users():
    async with async_session() as session:
        return await session.scalars(select(Blacklist.tg_id))

async def get_reason(tg_id):
    async with async_session() as session:
        return await session.scalar(select(Blacklist.reason).where(Blacklist.tg_id == tg_id))

async def get_datetime(datetime):
    async with async_session() as session:
        return await session.scalar(select(Blacklist.datetime).where(Blacklist.datetime == datetime))

async def get_chats():
    async with async_session() as session:
        return await session.scalars(select(Item.chat))

async def delete_ban(tg_id):
    async with async_session() as session:
        delete_query = delete(Blacklist).where(Blacklist.tg_id == tg_id)
        await session.execute(delete_query)
        await session.commit()

async def get_admins():
    async with async_session() as session:
        return await session.scalars(select(Admin.tg_id))

async def get_admin(tg_id):
    async with async_session() as session:
        return await session.scalar(select(Admin).where(Admin.tg_id == tg_id))
async def get_admins_nick():
    async with async_session() as session:
        return await session.scalars(select(Admin.username))

async def get_admin_serv(tg_id):
    async with async_session() as session:
        return await session.scalar(select(Admin.server).where(Admin.tg_id == tg_id))

async def get_admin_lvl(tg_id):
    async with async_session() as session:
        return await session.scalar(select(Admin.level).where(Admin.tg_id == tg_id))

async def get_leads():
    async with async_session() as session:
        return await session.scalars(select(Lead.tg_id))

async def set_admin(tg_id, username, server, level, pos):
    async with async_session() as session:
        await session.scalar(select(Admin).where(Admin.tg_id == tg_id))
        await session.scalar(select(Admin).where(Admin.username == username))
        await session.scalar(select(Admin).where(Admin.server == server))
        await session.scalar(select(Admin).where(Admin.level == level))
        await session.scalar(select(Admin).where(Admin.position == pos))
        session.add(Admin(tg_id=tg_id, username=username, server=server, level=level, position=pos))
        await session.commit()

async def del_admin(tg_id):
    async with async_session() as session:
        delete_query = delete(Admin).where(Admin.tg_id == tg_id)
        await session.execute(delete_query)
        await session.commit()

async def select_alladmins():
    async with async_session() as session:
        query = select(Admin).order_by(desc(Admin.level))
        result = await session.execute(query)
        admins = result.scalars().all()
        return admins

async def update_level(tg_id, level, pos):
    async with async_session() as session:
        update_query = update(Admin).where(Admin.tg_id == tg_id).values(level=level, position=pos)
        await session.execute(update_query)
        await session.commit()

async def set_meetings_info(tg_id, username, server, level, datetime, description):
    async with async_session() as session:
        await session.scalar(select(Mettings_Info).where(Mettings_Info.tg_id == tg_id))
        await session.scalar(select(Mettings_Info).where(Mettings_Info.username == username))
        await session.scalar(select(Mettings_Info).where(Mettings_Info.server == server))
        await session.scalar(select(Mettings_Info).where(Mettings_Info.level == level))
        await session.scalar(select(Mettings_Info).where(Mettings_Info.datetime_meeting == datetime))
        await session.scalar(select(Mettings_Info).where(Mettings_Info.description == description))
        session.add(Mettings_Info(tg_id=tg_id, username=username, server=server, level=level, datetime_meeting=datetime, description=description))
        await session.commit()

async def get_meetings_info(server):
    async with async_session() as session:
        query = select(Mettings_Info).where(Mettings_Info.server == server)
        result = await session.execute(query)
        meetings = result.scalars().all()
        return meetings

async def get_meeting_id(id):
    async with async_session() as session:
        return await session.scalar(select(Mettings_Info).where(Mettings_Info.id == id))

async def del_meeting(id):
    async with async_session() as session:
        delete_query = delete(Mettings_Info).where(Mettings_Info.id == id)
        await session.execute(delete_query)
        await session.commit()