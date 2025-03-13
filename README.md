# ChatCert 聊天機器人

這是一個使用 Azure OpenAI 服務的聊天機器人應用程式，基於 Flask 框架構建。為了保護敏感資訊，某些配置已被替換為佔位符。

## 專案結構

```
ChatCert/
├── app.py                # 主Flask應用程式
├── requirements.txt      # 依賴包列表
├── Terra.pem             # 憑證檔案(需要單獨配置)
├── templates/            # Flask模板目錄
│   └── index.html        # 聊天界面
├── static/               # Flask靜態文件目錄
│   ├── css/
│   │   └── style.css     # 樣式文件
│   └── js/
│       └── script.js     # JavaScript代碼
└── src/                  # 源碼目錄
```

## 環境設置

### 步驟 1: 克隆專案

```bash
git clone <repository-url>
cd ChatCert
```

### 步驟 2: 創建虛擬環境

#### Windows:

```bash
# 創建虛擬環境
python -m venv venv

# 啟用虛擬環境
venv\Scripts\activate
```

#### macOS / Linux:

```bash
# 創建虛擬環境
python3 -m venv venv

# 啟用虛擬環境
source venv/bin/activate
```

### 步驟 3: 安裝依賴

```bash
# 安裝所有依賴
pip install -r requirements.txt
```

## 恢復敏感資訊

在公司環境中使用本專案前，請恢復以下敏感資訊：

### 1. 代理設置

在`app.py`中尋找 `# CONFIG_SECTION: PROXY_SETTINGS` 部分，並替換為以下內容：

```python
# 如果 os.environ["no_proxy"] 最後一個元素是 "openai.azure.com"，則將 no_proxy 調整
if os.environ.get("no_proxy", "").split(",")[-1] == "openai.azure.com":
    os.environ["no_proxy"] = os.environ["no_proxy"] + ",openai.azure.com"

os.environ["http_proxy"] = "proxy...net:10443"
os.environ["https_proxy"] = "proxy...net:10443"
```

### 2. 認證資訊

在`app.py`中尋找 `# CONFIG_SECTION: AUTH_CREDENTIALS` 部分，並替換為以下內容：

```python
# Azure OpenAI 憑證設置 - 請在私有環境中填入真實認證資訊
# CONFIG_SECTION: AUTH_CREDENTIALS
client_id = "AE39708-..."     # 實際的客戶端ID
certificate_path = "Terra.pem"                        # 實際的憑證路徑
tenant_id = "79C73825-..."    # 實際的租戶ID
model = "gpt-4-2024-05-13"                           # 實際使用的模型名稱
```

### 3. Azure 端點

在`app.py`中尋找 `# CONFIG_SECTION: AZURE_ENDPOINT` 部分，並更新以下行：

```python
azure_endpoint="https://lmopenai.../"
```

### 4. 文件路徑設置

這一部分在簡化版應用中已被移除，無需配置。

## 確保憑證存在

請確保`Terra.pem`憑證文件位於專案根目錄。這個文件必須從您的公司安全來源獲取，不應該包含在公共代碼庫中。

## 啟動應用程式

在所有敏感資訊都已正確設置後，您可以通過以下命令啟動應用程式：

### Windows & macOS / Linux:

```bash
# 確保處於虛擬環境中
python app.py
```

應用程式將在`http://localhost:5000`啟動，您可以在瀏覽器中訪問此地址來使用聊天機器人。

## Azure OpenAI API 版本資訊

以下是可用的 Azure OpenAI API 預覽版本及其功能：

| API 版本           | 主要功能                             |
| ------------------ | ------------------------------------ |
| 2025-01-01-preview | 當前最新的預覽版本，支持預測輸出功能 |
| 2024-12-01-preview | 支持推理模型和存儲完成               |
| 2024-10-01-preview | 較早的預覽版本                       |
| 2024-05-01-preview | 支持助手 API V2                      |
| 2024-03-01-preview | 支持嵌入格式和維度參數               |
| 2024-02-15-preview | 支持助手 API 和文本轉語音            |

要更改 API 版本，請修改`app.py`中的`get_openai_instance()`函數：

```python
def get_openai_instance():
    """
    Create and return an Azure OpenAI client instance
    """
    client = AzureOpenAI(
        api_key=get_token(),
        api_version="2025-01-01-preview",  # 修改為所需的API版本
        azure_endpoint=azure_endpoint
    )
    return client
```

## 停止虛擬環境

當您完成工作後，可以通過以下命令離開虛擬環境：

#### Windows:

```bash
deactivate
```

#### macOS / Linux:

```bash
deactivate
```
