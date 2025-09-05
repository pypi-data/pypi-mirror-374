import os
import re

import autoflake
import autopep8
import isort


def modify_app_module(name: str, entity: str, path: str):
    db_name = "DbModule"
    module_name = f"{db_name}.for_feature({name.capitalize()})"
    app_path = os.path.join(path, f"{entity.lower()}_module.py")
    model_import_statement = f"from .{name.lower()}_model import {name.capitalize()}"
    db_module_import_statement = f"from nestipy_db import {db_name}"

    if os.path.exists(app_path):
        with open(app_path, "r") as file:
            file_content = file.read()
            file.close()
        # Check if the import statement already exists; if not, add it
        if model_import_statement not in file_content:
            file_content = model_import_statement + "\n" + file_content
        if db_module_import_statement not in file_content:
            file_content = db_module_import_statement + "\n" + file_content

        # Match the @Module decorator
        module_pattern = r"@Module\s*\(\s*(.*?)\s*\)\s*class"
        match = re.search(module_pattern, file_content, re.DOTALL)

        if match:
            module_body = match.group(1)
            imports_match = re.search(
                r"imports\s*=\s*\[\s*((?:[^\[\]]+|\[[^\[\]]*\])*)\s*\]",
                module_body,
                re.DOTALL,
            )

            if imports_match:
                # 'imports' exists; extract its content
                imports_content = imports_match.group(1).strip()

                # If the module is not already in the imports, add it
                if module_name not in imports_content:
                    if imports_content and not imports_content.endswith(","):
                        imports_content += ","  # Ensure comma before adding new import

                    new_imports = f"{imports_content}\n\t{module_name}"
                    updated_module_body = re.sub(
                        r"imports\s*=\s*\[\s*((?:[^\[\]]+|\[[^\[\]]*\])*)\s*\]",
                        f"imports=[\n\t{new_imports}\n]",
                        module_body,
                        flags=re.DOTALL,
                    )
                else:
                    updated_module_body = module_body
            else:
                # If 'imports' doesn't exist, add it to the @Module properties
                updated_module_body = (
                    module_body.strip() + f",\n\timports=[\n\t{module_name}\n]"
                )

            # Replace the old @Module body with the updated one
            updated_content = file_content.replace(module_body, updated_module_body)

            # Clean, sort, and format the final code
            cleaned_code = autoflake.fix_code(updated_content)
            sorted_code = isort.code(cleaned_code)
            formatted_code = autopep8.fix_code(sorted_code)

            # Write the updated content back to the file
            with open(app_path, "w") as file:
                file.write(formatted_code)
        else:
            print(f"No @Module decorator found in {entity.lower()}_module.py.")
