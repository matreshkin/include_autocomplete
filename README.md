# Include Autocomplete

A Sublime Text plugin that enables autocompletion for `.h` files in `#include`
directives.

## Settings

### Manual Setup

To add locations where the plugin should look for `.h` files, add the following
to your `.sublime-project` file:

```json
{
    "include_autocomplete_settings":
    {
        "include_locations":
        [
            {
                "path": "path/to/include/directory",
                "prefix": "directory",
            },
        ]
    }
}
```
