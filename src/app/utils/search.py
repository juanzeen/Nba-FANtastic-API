async def db_text_search(collection, query: str) -> list[dict]:
    cursor = (
        collection.find({"$text": {"$search": query}})
        .sort([("score", {"$meta": "textScore"})])
        .limit(10)
    )
    return await cursor.to_list()
