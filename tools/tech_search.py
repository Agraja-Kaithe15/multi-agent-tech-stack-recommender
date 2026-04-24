from tools.tech_catalog import tech_catalog_tool

def search_tech_stack(level):
    data = tech_catalog_tool()

    for item in data:
        if item["level"].lower() == level.lower():
            return item

    return {}