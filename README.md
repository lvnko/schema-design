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

### 1.4. Fact & Dimension

In data warehousing, a fact table consists of the measurements, metrics or facts of a business process.

It is located at the center of a star schema or a snowflake schema surrounded by dimension tables.

#### 1.4.1. Star Schema

The star schema consists of one or more fact tables referencing any number of dimension tables.

It is the approach most widely used to develop data warehouses and dimensional data marts.

#### 1.4.2. Snowflake Schema

The snowflake schema is similar to the star schema.

However, in the snowflake schema, dimensions are normalized into multiple related tables, whereas the star schema dimensions are denormalized with each dimension represented by a single table...

#### 1.4.3. Pros & Cons

<table>
  <thead>
    <tr>
        <th>種類</th>
        <th>Pros</th>
        <th colspan=2>Cons</th>
    </tr>
  </thead>
  <tbody>
    <tr>
        <td rowspan=2>Star Schema</td>
        <td>Simple Query</td>
        <td rowspan=2>Data Integrity Issue</td>
        <td rowspan=4>Fundemental not support to <b>Many-to-Many</b> data structure</td>
    </tr>
    <tr>
      <td>Fast Aggregation</td>
    </tr>
    <tr>
      <td rowspan=3>Snowflake Schema</td>
      <td rowspan=3>High Data Integrity</td>
      <td>Complex Query</td>
    </tr>
    <tr>
      <td>Slow Aggregation</td>
    </tr>
  </tbody>
</table>

## 2. 實作：資料庫架構優化


- Porgram Implementation (九) — 教程裡面出錯的原因是因為在用 bad_comments 裡的 post_id 到舊 post table (bad_posts) 裡提取出來的 title 有一些是超過 100 個 characters 的，這不符合新 post table, posts 中 title 的規格，因此而找不到對應的 post_id。

## 3. 指令

```shell
docker cp <local_file> <container_name>:<container_path>
```
