# BDD File Client

BDD 平台文件服务客户端

## 安装方式

```shell
$ pip install bdd-file-client
```

## 快速开始

### 配置 BddFileClient

```python
from bdd_file import BddFileClient, UploadMode

client = BddFileClient(
    profile="dev",            # 可选 dev、beta、prod，默认为 dev
    default_user_id="114514", # 默认的用户 ID，可在调用时覆盖
    default_biz="chat",       # 默认的业务类型，可在调用时覆盖
    default_mode=UploadMode.AUTO,  # 默认的上传模式，可在调用时覆盖
)
```

- `profile` 用于指定后端环境，会自动映射到对应的服务地址
- `default_user_id`、`default_biz`、`default_mode` 均为可选，若在调用时未显式提供则使用此处的默认值

### 上传文件

```python
# 1. 通过文件路径上传（简单上传）
result = client.upload(
    path="example.png",
    mode=UploadMode.SIMPLE,   # 默认 auto，可选 simple、multipart
    biz="chat",
    biz_params={"chat_id": "191810"},
)
print("上传成功，file_id =", result.file_id)

# 2. 通过文件流上传
with open("example.png", "rb") as f:
    result = client.upload(
        stream=f,
        filename="example.png",           # 当使用 stream 时，必须显式指定文件名
        size=1024,                        # 当使用 stream 时，必须显式指定文件大小
        biz="chat",
        biz_params={"chat_id": "191810"},
    )

# 3. 自动选择上传模式
result = client.upload(
    path="large_file.zip",  # 文件大于 100MB 时自动使用分片上传
    mode=UploadMode.AUTO,   # 默认值
    biz="chat",
    biz_params={"chat_id": "191810"},
)
```

注意：
- `path` 与 `stream` 只能二选一
- 使用 `stream` 时必须同时提供 `filename` 和 `size`
- 当文件大小超过 100MB 时，建议使用 `UploadMode.MULTIPART` 模式以支持断点续传
- 上传模式说明：
  - `SIMPLE`: 简单上传，不支持断点续传
  - `MULTIPART`: 分片上传，支持断点续传
  - `AUTO`: 自动选择上传模式，如果文件大于 100MB，则使用分片上传，否则使用简单上传

### 下载文件

```python
# 1. 保存到本地文件
client.download(
    file_id=result.file_id,
    path="downloaded.png",
)

# 2. 写入到自定义流
from io import BytesIO

buffer = BytesIO()
client.download(file_id=result.file_id, stream=buffer)
print(buffer.getvalue())

# 3. 获取下载链接（支持设置过期时间）
url = client.get_download_url(
    file_id=result.file_id,
    expires_seconds=600,  # 链接有效期，默认 10 分钟
)
print("下载链接：", url)
```

注意：
- `path` 与 `stream` 只能二选一
- 下载链接默认有效期为 10 分钟，可通过 `expires_seconds` 参数调整
- 下载链接支持直接通过 HTTP 请求访问

### 文件管理

```python
# 1. 删除文件
client.delete(file_id=result.file_id)

# 2. 获取聊天文件列表
files = client.list_chat_files(chat_id="191810")
for file in files:
    print(f"文件ID: {file.id}, 文件名: {file.filename}")
```

### 同步聊天文件

```python
# 1. 将聊天文件同步到本地
results = client.sync_chat_files_to_local(
    chat_id="191810",
    local_dir="./downloads",  # 本地目录路径
)
for file_id, result in results.items():
    if result.is_success:
        print(f"文件 {file_id} 同步成功：{result.local_path}")
    else:
        print(f"文件 {file_id} 同步失败：{result.error_message}")

# 2. 将本地文件同步到聊天
results = client.sync_chat_files_to_remote(
    chat_id="191810",
    local_dir="./uploads",  # 本地目录路径
)
for file_path, result in results.items():
    if result.status == "success":
        print(f"文件 {file_path} 上传成功，file_id = {result.file_id}")
    elif result.status == "skipped":
        print(f"文件 {file_path} 已存在，跳过")
    else:
        print(f"文件 {file_path} 上传失败：{result.error_message}")
```

同步规则说明：
1. 同步到本地：
   - 支持并发下载，提高效率
   - 会覆盖同名的本地文件
   - 每个文件都会返回同步结果，包含成功/失败状态和错误信息

2. 同步到远程：
   - 支持并发上传，提高效率
   - 根据文件名判断是否需要同步：
     - 本地和远程都存在，跳过
     - 本地存在，远程不存在，上传
     - 本地不存在，远程存在，跳过
   - 每个文件都会返回同步结果，包含状态（success/skipped/failed）、文件ID和错误信息

#### 列出目录

```python
# 获取目录列表
paged = client.list_directories(page_size=5, page_number=1)
for directory in paged.items:
    print(f"目录ID: {directory.id}, 目录名: {directory.name}")
```
- 支持按名称、排序方式、分页等参数筛选

#### 列出目录下的文件

```python
# 获取指定目录下的文件列表
directory_id = 123  # 替换为实际目录ID
paged = client.list_files_in_directory(directory_id=directory_id, page_size=10, page_number=1)
for file in paged.items:
    print(f"文件ID: {file.id}, 文件名: {file.filename}")
```
- 支持按排序方式、分页等参数筛选

### 错误处理

所有业务及网络错误都会抛出 `bdd_file.BddFileError`，可按需捕获：

```python
from bdd_file import BddFileClient, BddFileError

client = BddFileClient(default_user_id="114514")
try:
    result = client.upload(path="not_exists.txt", biz="chat")
except BddFileError as e:
    print("操作失败：", e)
```

### 注意事项

1. 所有需要 `user_id` 的方法都支持在调用时覆盖默认值
2. 同步文件到远程时，会根据文件名判断是否需要同步：
   - 本地和远程都存在，跳过
   - 本地存在，远程不存在，上传
   - 本地不存在，远程存在，跳过
3. 文件列表接口支持分页，会自动获取所有数据
4. 同步文件操作支持并发处理，提高效率
