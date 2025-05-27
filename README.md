# Week #027

資料庫架構規劃

## 1. Schema 設計

### 1.1. CONSTRAINT

#### 1.1.1. CONSTRAINT
* PRIMARY KEY
* NULL or NOT NULL

#### 1.1.2. Check
可在 ``CHECK`` 後面的 ``(...)`` 中輸入

#### 1.1.3. Foreign Key - On Delete Constraint
* On Delete Restrict
* On Delete Cascade
* On Delete Set Null

### 1.2. 資料庫正規化 (Normalization)

#### 1.2.1. 第一層 Normalization (1st Normal Form)
* Consistent Type — 讓每個欄內的值都務求是同樣的型別，然後除了型別，也需要求格式的ㄧ致，如：大小寫、時間日期格式
* Single Value — 讓每個欄內的資料都必須為單一的值，並讓多出的值分欄位或，在挪到另一個表格去做多行處理，如：用戶表格中的用戶有時擁有多過一個的聯絡電話，這時這些電話號碼就要在另外一個表格分行處理
* No Repeated Column — 把重複屬性的欄位歸納為一，然後分行處理 (row based)
* Unique Row — 在表格內，每行都必須要有，或透過值的組合來造出，獨立的 Primary Key

#### 1.2.2. 第二層 Normalization (2nd Normal Form)
* Must be at 1st Normal Form — 必須符合第一層正規化的要求
* No Partial Dependency — 當表格內某些欄位的值是取決於部分或某一欄位 (UNIQUE ID PRIMARY KEY 除外) 的值來定義，那麼它是應該被分開到另一個表格去管理的，相反，若一欄位的值是取決於全行的所有其他欄位值的組合，便沒有問題

#### 1.2.3. 第三層 Normalization (3rd Normal Form)
* Must be at 2nd Normal Form — 必須符合第二層正規化的要求
* No Transitive Dependency — 跟 No Partial Dependency 的規則有一定的類似，當一個欄位的值是取決於 PRIMARY KEY 以外的其他欄位值，那麼就會造成連鎖的相依關係。例：employee_name -> employee_id -> id，由前例可以看到，employee_name 是可以從表格中抽出來由另外一個表格來儲存的。

### 1.3 Data Integrity 管理

資料完整性是指資料的有效性和可靠性，意味著您的資料是準確、完整、一致且安全的。資料完整性之所以重要，原因有很多，例如確保分析、報告和決策的正確性，防止資料遺失或損壞，以及符合法規和標準。資料完整性可能會因人為錯誤、系統故障、惡意攻擊或不良設計而受到損害。

### 1.4 Entity Concepts

在資料庫設計中，實體（Entity）代表一個真實世界的物件或概念，關於它儲存了資料。例子包括人、地點、事件或概念。實體具有描述其屬性的特性。在關聯式資料庫中，實體通常表示為一個表格，其屬性表示為該表格中的欄位。實體之間存在關係，表明它們是如何連接的。這些關係對於設計一個結構良好的資料庫架構至關重要。

### 1.5. 事實與維度 (Fact & Dimension)

在資料倉儲中，事實表包含業務流程的測量、指標或事實。

它位於星型模式或雪花型模式的中心，周圍環繞著維度表。

#### 1.5.1. 星型模式 (Star Schema)

星型模式由一個或多個事實表組成，這些事實表引用任意數量的維度表。

它是開發資料倉儲和維度資料超市最廣泛使用的方法。

#### 1.5.2. 雪花型模式 (Snowflake Schema)

雪花型模式與星型模式相似。

然而，在雪花型模式中，維度被正規化為多個相關表，而星型模式的維度則被反正規化，每個維度由一個單獨的表表示...

#### 1.5.3. 優缺點 (Pros & Cons)

<table>
  <thead>
    <tr>
        <th>種類</th>
        <th>優點 (Pros)</th>
        <th colspan=2>缺點 (Cons)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
        <td rowspan=2>星型模式 (Star Schema)</td>
        <td>查詢簡單 (Simple Query)</td>
        <td rowspan=2>資料完整性問題 (Data Integrity Issue)</td>
        <td rowspan=4>基本不支援<b>多對多</b>資料結構 (Fundamental not support to <b>Many-to-Many</b> data structure)</td>
    </tr>
    <tr>
      <td>聚合快速 (Fast Aggregation)</td>
    </tr>
    <tr>
      <td rowspan=3>雪花型模式 (Snowflake Schema)</td>
      <td rowspan=3>高資料完整性 (High Data Integrity)</td>
      <td>查詢複雜 (Complex Query)</td>
    </tr>
    <tr>
      <td>聚合緩慢 (Slow Aggregation)</td>
    </tr>
  </tbody>
</table>

## 2. 實作：資料庫架構優化

### 2.1. 資料遷移工具 (Data Migration Tools)

本專案使用 `TableMigrator` 和 `RecycleLogger` 兩個工具類別來協助資料遷移過程。

#### 2.1.1. TableMigrator

`TableMigrator` 類別用於處理從來源到目標表的批次資料遷移。它支援分批處理、資料轉換和驗證。

**主要功能:**

*   **初始化 (`__init__`):** 接受資料庫連線配置、批次大小、查找資料總筆數限制、與是否開啟測試模式作為參數。
*   **遷移表格 (`migrate_table`):** 執行資料遷移。接受來源查詢、插入查詢、來源參數、驗證函數和轉換函數。它會分批從來源資料庫讀取資料，對每行資料進行可選的驗證和轉換，然後將處理後的資料插入到目標資料庫。

**使用範例 (詳見 `data_migration/main.py`):**

在 `data_migration/main.py` 中，`TableMigrator` 被用於遷移 `topics`, `posts`, `comments`, 和 `votes` 等表格。以下是一個遷移 `topics` 的簡化範例：

```python
migrator = TableMigrator(conn_config=config["postgres"])

def validate_func(row):
    # 驗證邏輯
    return True

def transform_func(row):
    # 轉換邏輯
    return (row["topic"], row["user_id"])

total_migrated = migrator.migrate_table(
    source_query=select_sql,
    insert_query=insert_sql,
    transform_func=transform_func,
    validate_func=validate_func
)
```

#### 2.1.2. RecycleLogger

`RecycleLogger` 類別用於記錄在資料遷移過程中因各種原因（如資料不符合新架構要求）而無法遷移的資料。這些記錄可以幫助後續的資料清理或分析。

**主要功能:**

*   **初始化 (`__init__`):** 接受記錄檔的路徑作為參數。
*   **記錄 (`log`):** 記錄無法遷移的資料的詳細資訊，包括目標表、值、來源、是否可回收以及缺失的原因。

**使用範例 (詳見 `data_migration/main.py`):**

在 `data_migration/main.py` 中，`RecycleLogger` 被用於記錄在遷移 `posts`, `comments`, 和 `votes` 時遇到的無效或缺失資料。以下是一個記錄無效 `post` 的簡化範例：

```python
recycle_logger = RecycleLogger(f"{dir_path}/logs/recycle.csv")

def validate_func(row):
    if row["title"] is None:
        recycle_logger.log(
            recycle_to="posts",
            value=id,
            came_from="bad_posts.id",
            can_be_recycle=False,
            missing='title'
        )
        return False
    # 其他驗證邏輯
    return True
```

## 3. 指令

```shell
# 如何把需要用的檔案搬運到 container 裡面
docker cp <local_file> <container_name>:<container_path>
```

## 4. 有用資源
- 一篇關於 Psycopg2 Server Side Cursor Itersize 用法的討論 [[連結](https://stackoverflow.com/questions/63623336/how-does-psycopg2-server-side-cursor-operate-when-itersize-is-less-than-data-siz)]
