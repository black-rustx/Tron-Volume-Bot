# 🦖 **Tron Volume Bot**  

## 🚀 Quick Setup  

1. **Create a Virtual Environment**:  
   ```bash
   python -m venv venv
   ```  

2. **Activate the Virtual Environment**:  
   - 🐧 **Linux**:  
     ```bash
     source venv/bin/activate
     ```  
   - 🪟 **Windows**:  
     ```bash
     .\venv\Scripts\activate.bat
     ```  

3. **Install Dependencies**:  
   ```bash
   pip install -r requirements.txt
   ```  

4. **Run the Bot**:  
   ```bash
   python solid_trex.py
   ```  

---

## 🌐 **Usage**  

### 🔑 **API Key Setup**  
- To use this bot on the **mainnet**, obtain an API key from [TronGrid.io](https://www.trongrid.io/).  
- **Demo Mode** (Testnet): No API key is required.  

---

## 📤 **TRX Sender**  

A file named `trx_sender.py` is included in the folder.  
### ✨ Features:  
- Sends all TRX balances from wallets to a specified main address.  
- Usage:  
  ```bash
  python trx_sender.py
  ```  

  - **Input Required**:  
    1. Enter the **main address** you want to send TRX to.  
    2. Provide the **wallet file name** (e.g., `wallets1.txt`).  

  - **Example**:  
    If the file `wallets1.txt` contains wallet addresses, all TRX balances will be sent to the specified main address.  

---

## ⚠️ **Important Notes**  

1. **⏳ Delay Settings**  
   - Always set a **minimum delay of 10 seconds** to avoid errors.  

2. **💰 Trade Amounts**  
   - Ensure that `min_trade_amount` and `max_trade_amount` values comply with the exchange's minimum requirements.  
   - **Tip**: Test on the **Testnet** before using on **Mainnet**.  

---

## 🛑 **Disclaimer**  
> **Warning**:  
> You are solely responsible for any capital loss when using this bot. Please proceed with caution.  

---

Let me know if you'd like to add more details or features! 😊
