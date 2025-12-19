# Line Width Variator (線寬變異產生器)

這是一個用於在 Ansys EDB 檔案中產生線寬變異（波浪線）的工具，旨在模擬製程粗糙度並分析其對訊號完整性的影響。

## 功能特色

*   **離線產生 (Offline Generation)**：即時預覽變異效果，無需修改原始 EDB 檔案。
*   **互動式視覺化**：直接在應用程式中查看產生的波浪線。
*   **統計面板 (Statistics Panel)**：分析產生變異的統計特性（如標準差、平均寬度）。
*   **訊號線過濾**：自動識別並僅對訊號線 (Signal Nets) 應用變異。
*   **非破壞性工作流**：原始 EDB 檔案保持不變。只有在執行「另存新檔 (Save As)」時才會應用變更。
*   **工作階段還原**：儲存變異後，自動重新開啟原始 EDB，方便快速進行多次迭代實驗。

## 系統需求

*   **Ansys Electronics Desktop**：需安裝並取得授權（建議版本 2024.1 或更高）。
*   **Python**：3.10 或更高版本。
*   **uv**：快速的 Python 套件安裝與解析工具。（`run.bat` 腳本若發現未安裝會嘗試自動安裝）。

## 安裝與設定

1.  **複製儲存庫 (Clone Repository)**：
    ```bash
    git clone <repository-url>
    cd line-width-variator
    ```

2.  **執行應用程式**：
    在 Windows 上直接雙擊 `run.bat` 即可。
    
    或者透過終端機執行：
    ```bash
    run.bat
    ```

    該腳本會自動執行以下步驟：
    *   檢查 `uv` 是否安裝，若無則自動安裝。
    *   同步 Python 環境與相依套件。
    *   啟動應用程式。

## 使用說明

1.  **開啟 EDB**：
    *   點擊左側邊欄的 **Open** 按鈕。
    *   選擇現有的 `.aedb` 資料夾。

2.  **選擇圖元 (Primitive)**：
    *   在主視圖中點擊選取一條走線。
    *   底部中央的 **Stats Panel** 將顯示其當前的屬性。

3.  **設定參數**：
    *   使用左側邊欄的 **Settings Panel** 調整產生參數：
        *   `AEDB Version`：使用的 Ansys Electronics Desktop 版本（例如 "2024.1", "2023.2"）。
        *   `Sigma_w (%)`：**線寬變異幅度**。線寬變異的標準差，以原始線寬的百分比表示。數值越高，寬度變化越明顯。
        *   `L_c`：**相關長度 (Correlation Length)**。控制線寬沿著走線變化的快慢。
            *   較小的 `L_c`：快速、高頻的變化（較粗糙）。
            *   較大的 `L_c`：緩慢、平滑的變化。
        *   `Model`：**統計模型**。用於產生隨機變異的共變異數函數。
            *   `Gaussian`：非常平滑的變異。
            *   `Exponential`：較粗糙、相關性較低的變異。
            *   `Matern32`：介於 Gaussian 和 Exponential 之間（通常較符合實際製程粗糙度）。
        *   `ds_arc`：**離散化步長**。產生圓弧時的最大線段長度。數值越小曲線越平滑，但檔案大小和處理時間會增加。
        *   `n_resample`：**重取樣點數**。在映射到走線幾何之前，用於產生初始隨機輪廓的點數。
        *   `w_min` / `w_max`：**寬度限制**。最小與最大寬度的硬性限制，以原始寬度的百分比表示。這可以防止走線變得太細（開路風險）或太寬（短路風險）。

4.  **產生變異 (Generate)**：
    *   點擊 Settings Panel 底部的 **Generate** 按鈕。
    *   視圖將更新並顯示波浪線。
    *   Stats Panel 將更新並顯示所選圖元的新統計數據。

5.  **儲存變異 (Save Variation)**：
    *   點擊左側邊欄的 **Save As**。
    *   選擇新的 `.aedb` 檔案位置/名稱（例如 `project_var1.aedb`）。
    *   應用程式將把變異儲存到新檔案中，然後自動還原至原始 EDB，讓您可以繼續進行實驗。

## 開發模式

若要在開發模式下執行（支援熱重載）：

1.  **前端 (Frontend)**：
    ```bash
    cd frontend
    npm install
    npm run dev
    ```

2.  **後端 (Backend)**：
    ```bash
    # 在另一個終端機中，於專案根目錄執行
    uv run app.py
    ```
