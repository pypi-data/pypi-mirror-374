# {plugin_id} Capture Plugin

This is a template for a capture plugin for the [Multimodal Observer](https://github.com/MultimodalObserver-2/mo) software.

## 🧩 Structure
<pre>
{plugin_id}/
├── src/
│   └── {plugin_id}/
│       ├── main.py           # Main plugin class, implements CapturePlugin
│       └── properties.py     # Property definitions (UI/configuration)
├── metadata.json             # Plugin manifest (edit name, description, author, etc)
├── requirements.txt          # Python dependencies (edit as needed)
├── icons/
│   ├── dark.svg
│   └── light.svg
├── locales/
│   └── en/
│       └── {plugin_id}.json  # English translations (edit/add keys as needed)
├── .gitignore
</pre> 

## 🚀 Getting Started

1. **Edit `metadata.json`**  
   - Set plugin name, description, author, repository, etc.
   - The `entryPoints` section must match your class and file names.

2. **Implement your logic in `main.py`**  
   - Inherit from `CapturePlugin` and implement all required methods.
   - Add any dependencies to `requirements.txt`.

3. **Define properties in `properties.py`**  
   - Add configuration fields using the `Properties` class.
   - Use `translate()` for labels and provide translation keys in your locale file.

4. **Add your plugin icons**  
   - Replace `icons/dark.svg` and `icons/light.svg` with your own.

5. **Provide translations**  
   - Edit `locales/en/{plugin_id}.json` for UI/config texts.

6. **Install dependencies (optional)**  
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt

## 📝 Example: Adding a property

In `properties.py`:
```python
from mo import translate

properties.add_bool("my_flag", translate("property.my_flag"))
properties.set_default("my_flag", True)
```

In `locales/en/{plugin_id}.json`:
```json
{
    "property.my_flag": "Enable advanced capture mode"
}
```

## 📦 Build & Package

- Use the MO plugin builder CLI to package your plugin for distribution:
```bash
  build-mop --entry . --output dist/
```
- See the MO documentation for details on packaging, registration, and testing.