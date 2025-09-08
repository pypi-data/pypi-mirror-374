<h1 align="center">🚀 Teloxi: Based on Telethon, with additional features and easier usage</h1>

<p align="center">
<a href="https://pypi.org/project/teloxi/"><img src="https://img.shields.io/pypi/v/teloxi?style=plastic" alt="PyPI - Version"></a>
<a href="https://github.com/abbas-bachari/teloxi"><img src="https://img.shields.io/badge/Python%20-3.8+-green?style=plastic&logo=Python" alt="Python"></a>
  <a href="https://pypi.org/project/teloxi/"><img src="https://img.shields.io/pypi/l/teloxi?style=plastic" alt="License"></a>
  <a href="https://pepy.tech/project/teloxi"><img src="https://pepy.tech/badge/teloxi?style=flat-plastic" alt="Downloads"></a>
</p>

## 🛠️ Version: 1.0.1

## 🌟 **Introduction**

### **Teloxi** is a lightweight, easy-to-use library based on Telethon, with additional features and easier usage.  

## ✨ Features

**Teloxi** is a user-friendly Python library built on top of Telethon, offering enhanced Telegram automation capabilities. Key features include:

- 🖥️ **Multi-session management**: Easily store, retrieve, update, and delete multiple Telegram accounts.  
- 🔑 **Login code handling**: Automatically fetch Telegram login codes via BotFather interaction.  
- 🗄️ **Database integration**: Store sessions in SQLite or other supported storage backends.  
- 📊 **Query filtering & sorting**: Retrieve sessions using advanced filtering, ordering, and limit options.  
- ⚡ **Asynchronous support**: Fully async functions for high-performance Telegram operations.  
- 📱 **Multi-platform Device support**: Compatible with Telegram Device for **Android, Windows, Linux, macOS, and iOS**.  
- 🛠️ **Extensible & open-source**: Easy to customize and contribute additional features.  

> Designed to simplify Telegram automation and make multi-account management effortless.


---

## 📚 **Requirements**

* **[Python 3.10+](https://python.org)**
* **[telethon 1.41.2+](https://pypi.org/project/telethon)**
* **[dbflux 1.0.2+](https://pypi.org/project/dbflux)**

---

## 🔧 **Installation**

Install **teloxi** via **pip**:

```bash
pip install teloxi
```

Or install from source:

```bash
git clone https://github.com/abbas-bachari/teloxi.git
cd teloxi
pip install .

```

---

## 💡 **Quick Start**

```python
import asyncio
from dbflux import Sqlite
from proxa import ProxyManager
from teloxi import TeloxiClient,Device,Storage


proxa=ProxyManager(['http://127.0.0.1:10808','socks5://127.0.0.1:1080'])
DB=Storage(Sqlite('sessions.ses'))


proxy=proxa.get_working_proxy()

async def main():
    session_id='+19223338123'

    
    client=TeloxiClient(
                        session_id=session_id, 
                        database=DB,
                        device=Device.TelegramAndroid.Generate(),
                        proxy=proxy.for_telethon
                        )
    

    await client.connect()
   
    is_auth=await client.is_user_authorized()
    if not is_auth:
        await client.start(phone=p)
  
    
    await client.PrintSessions()
    

    me=await client.get_full_me()

    print(f"Phone    : {me.phone}")
    print(f"User ID  : {me.id}")
    print(f"Username : {me.username or ''}")
    print(f"Full Name: {me.first_name} {me.last_name or ''}")
    print(f"About    : {me.about}")
    
   

    chat_info,error,is_joined= await client.join_chat('https://t.me/+2Rllq4qAlvk4MjM0')
    if is_joined:
       
       print(f"Success join to {chat_info.__class__.__name__}: {chat_info.title } ")
    else:
        print(f"{ error.__class__.__name__}: {error}")
        
    
    await client.disconnect()

    
if __name__=="__main__":
    asyncio.run(main())

```

### 💻 Output:

```shel
|---------+---------------------+----------+------------+--------+--------------------------+--------------|
|         |       Device        | Platform |   System   | API_ID |         App name         | Official App |
|---------+---------------------+----------+------------+--------+--------------------------+--------------|
| Current | Samsung Galaxy S25  | Android  |  13 (33)   |   6    | Telegram Android 11.14.1 |      ✔       |
|---------+---------------------+----------+------------+--------+--------------------------+--------------|
|    1    | Redmi Redmi Note 9S | Android  |  12 (31)   |   6    | Telegram Android 11.14.1 |      ✔       |
|    2    |  Samsung Galaxy S3  | Android  | 8.0 O (26) |   6    | Telegram Android 11.13.2 |      ✔       |
|---------+---------------------+----------+------------+--------+--------------------------+--------------|
Phone    : +19223338123
User ID  : 46567598
Username : usernam_2
Full Name: user-2 telegram
About    : None
Success join to Channel: Test Channel 
```

---

## 🗄️ Connect to Saved Sessions

```python
import asyncio
from dbflux import Sqlite
from proxa import ProxyManager
from teloxi import TeloxiClient,Device,Storage,Account


proxa=ProxyManager(['http://127.0.0.1:10808','socks5://127.0.0.1:1080'])
DB=Storage(Sqlite('sessions.ses'))

async def main():
    proxy=proxa.get_working_proxy()
    accounts: list[Account]=DB.get(limit=5,conditions=[Account.status=='ACTIVE'])
    for account in accounts:
        
        client=TeloxiClient(session_id=account.session_id,database=DB,proxy=proxy.for_telethon) 
        await client.connect()
        
        
        
        me=await client.get_me()
        
        if me:
            print(f"Phone    : {me.phone}")
            print(f"User ID  : {me.id}")
            print(f"Username : {me.username or ''}")
            print(f"Full Name: {me.first_name} {me.last_name or ''}")
            print("="*30)
            

        await client.disconnect()
        await asyncio.sleep(5)

if __name__=="__main__":
    asyncio.run(main())

```

### 💻 Output:

```shell
Phone    : 9812356488
User ID  : 46567598
Username : username_1
Full Name: user-1
==============================
Phone    : +19223338123
User ID  : 5865442887
Username : usernam_2
Full Name: user-2 telegram
==============================
Phone    : 1923155554
User ID  : 8320041566
Username : usernam_2
Full Name: user-3
==============================
```

---

### 🔑 Get Login Code

```python
async def code_callback(message, code):
    if code:
        print(f"Received login code: {code}")
    else:
        print(message)


async def main():
    proxy = proxa.get_working_proxy()
    session_id = '+1987654321'

    client = TeloxiClient(
        session_id=session_id, 
        database=DB,
        proxy=proxy.for_telethon
    )

    await client.connect()
   
    is_auth = await client.is_user_authorized()
    if is_auth:
        code = await client.get_login_code(callback=code_callback)
        if code:
            print(f"Login code successfully retrieved: {code}")
        else:
            print("Failed to get login code.")


if __name__ == "__main__":
    asyncio.run(main())

```

### 💻 Example Output

```shell
Login to +1987654321 now to grab your code!
Received login code: 86305
Login code successfully retrieved: 86305

```

---

## 🗄️ Manage Saved Sessions

```python
# Initialize sessions manager
DB = Storage(base_db=Sqlite('sessions.ses'))
session_id = '+1987654321'

# ------------------------------
# Get a single session by session_id
accounts: list[Account] = DB.get(conditions=[Account.session_id == session_id])
if accounts:
    account = accounts[0]
    print(f"Name: {account.first_name:<15} | Is bot: {'YES' if account.is_bot else 'NO':<3} | status: {account.status}")

# ------------------------------
# Get all sessions
accounts: list[Account] = DB.get()
for account in accounts:
    print(f"Name: {account.first_name:<15} | Is bot: {'YES' if account.is_bot else 'NO':<3} | status: {account.status}")

# ------------------------------
# Get active sessions
active_sessions: list[Account] = DB.get(conditions=[Account.status == "ACTIVE"])

# Get inactive sessions
inactive_sessions: list[Account] = DB.get(conditions=[Account.status == "INACTIVE"])

# Get bot sessions
bot_sessions: list[Account] = DB.get(conditions=[Account.is_bot == True])

# ------------------------------
# Get first 5 active non-bot sessions
first_5_sessions: list[Account] = DB.get(limit=5, conditions=[Account.status == "ACTIVE", Account.is_bot == False])

# ------------------------------
# Get random sessions (example: 3 active non-bot)
random_sessions: list[Account] = DB.get(limit=3, conditions=[Account.status=="ACTIVE", Account.is_bot==False], random=True)

# ------------------------------
# Delete all bot sessions
deleted_bots = DB.delete(conditions=[Account.is_bot == True])
print(f'Deleted {deleted_bots} bot sessions!')

# Delete all sessions
deleted_all = DB.delete(conditions='ALL')
print(f'Deleted {deleted_all} sessions!')

# Delete inactive sessions
deleted_inactive = DB.delete(conditions=[Account.status == "INACTIVE"])
print(f'Deleted {deleted_inactive} inactive sessions!')

# ------------------------------
# Update bot sessions to inactive
updated_bots = DB.update(conditions=[Account.is_bot == True], data={'status':'INACTIVE'})
print(f'Updated {updated_bots} bot sessions!')

# Update a specific session by phone
updated_one = DB.update(conditions=[Account.phone == '+9811111'], data={'status':'INACTIVE'})
print(f'Updated {updated_one} session!')
```

---

### 💻 Example Output

```shell
Name: user-1         | Is bot: NO  | status: ACTIVE
Name: user-2         | Is bot: YES | status: INACTIVE
Name: user-3         | Is bot: NO  | status: ACTIVE
...
Deleted 2 bot sessions!
Deleted 10 sessions!
Updated 3 bot sessions!
Updated 1 session!
```

---

## 👤 About the Author

**Abbas Bachari / عباس بچاری** – Developer & Maintainer of **Teloxi**

- 📧 Telegram: [@abbas_bachari](https://t.me/abbas_bachari)  
- 🌐 GitHub: [github.com/abbas-bachari](https://github.com/abbas-bachari)
