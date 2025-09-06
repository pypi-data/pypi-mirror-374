Here’s a polished version of your README with improved grammar, clearer instructions, and some additional helpful details:

---

### Usage

#### 1. Install Sheetrika
1. Create a virtual environment (recommended to isolate dependencies):
   ```sh
   python3 -m venv .venv
   ```
2. Install Sheetrika inside the virtual environment:
   ```sh
   .venv/bin/pip install sheetrika
   ```

#### 2. Enable Google Sheets API
1. Go to the [Google Cloud Console API Library](https://console.cloud.google.com/apis/library).
2. Search for `Google Sheets API`.
3. Click **Enable** to activate the API for your project.

#### 3. Create a Service Account
1. Navigate to the [Google Cloud Console Credentials page](https://console.cloud.google.com/apis/credentials).
2. Click **Create Service Account** and follow the prompts.
3. In the Service Account settings, go to the **Keys** tab and click **Add Key** → **JSON**. Save the file as `creds.json`.
4. Encode the credentials for secure use:
   ```sh
   .venv/bin/sheetrika encode creds.json
   ```
5. Copy the output and save it to a new `.env` file. Example:
   ```sh
   export GOOGLE_API_TOKEN="your_encoded_token_here"
   ```

#### 4. Configure Demo Parameters in `config.yml`
1. **Google Spreadsheet Setup**:
   - Create a new spreadsheet or open an existing one.
   - Extract the `spreadsheet_id` from the URL:
     ```
     https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit
     ```
   - Add the `client_email` from `creds.json` to the spreadsheet’s sharing permissions (as an editor).
2. **Yandex Metrica Parameters**:
   - Refer to the [Yandex Metrica Documentation](https://yandex.ru/dev/metrika/ru/stat/openapi/data) for query parameters.

Example `config.yml`:
```yaml
tasks:
  - name: live_demo__y_metrica
    query:
      url: https://api-metrika.yandex.ru/stat/v1/data/bytime.csv
      params:
        date1: 3daysAgo
        date2: today
        id: <your_metrica_counter_id>
        metrics: ym:s:visits,ym:s:users
        dimensions: ym:s:TrafficSource
        group: day
        filters: ym:s:isRobot=='No'
      schema:
        - Период
        - Переходы из поисковых систем
        - Переходы по ссылкам на сайтах
        - Прямые заходы
        - Внутренние переходы
        - Переходы из социальных сетей
        - Переходы из рекомендательных систем
    sheet:
      spreadsheet_id: <your_spreadsheet_id>
      name: main
      range: A2
      wtype: merge
```

#### 5. Get a Yandex API Token
1. Follow the [Yandex Metrica Authorization Guide](https://yandex.ru/dev/metrika/ru/intro/authorization) to obtain a token.
2. Save the token to your `.env` file:
   ```sh
   export YANDEX_API_TOKEN="your_yandex_token_here"
   ```

#### 6. Run the Example
Load the environment variables and execute the script:

```python
import os
from sheetrika.loader import SheetrikaLoader

def main():
    loader = SheetrikaLoader(
        ym_token=os.getenv('YANDEX_API_TOKEN'),
        goo_token=os.getenv('GOOGLE_API_TOKEN'),
        config_path='config.yaml',
    )
    loader.run()

if __name__ == '__main__':
    main()
```

#### Writing Types (`wtype` Options)
1. **`snapshot`**: Clears all data in the specified range and writes new data.
2. **`append`**: Finds the first empty row and appends data below it.
3. **`merge`**: Matches values in the first column and updates non-intersecting rows.

---

### Additional Notes:
- **Virtual Environment**: Always activate your virtual environment before running commands:
  ```sh
  source .venv/bin/activate  # Linux/Mac
  .venv\Scripts\activate     # Windows
  ```
- **Security**: Keep `creds.json` and `.env` files out of version control (add them to `.gitignore`).
- **Debugging**: If permissions fail, ensure the `client_email` has edit access to the spreadsheet.

Let me know if you'd like further refinements!
