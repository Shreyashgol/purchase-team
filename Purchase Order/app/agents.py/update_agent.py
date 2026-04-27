from fastapi import HTTPException


def execute(intent, repository):
    del repository

    if not intent.docEntry:
        raise HTTPException(
            status_code=400,
            detail="DocEntry is required to update a purchase order. Example: 'Update purchase order 12345'",
        )

    raise HTTPException(status_code=501, detail="Update operation not yet implemented")
