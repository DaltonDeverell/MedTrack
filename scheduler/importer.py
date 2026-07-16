import pandas as pd
import sqlite3


def import_curriculum(excel_file, database):

    workbook = pd.ExcelFile(excel_file)

    conn = sqlite3.connect(database)
    cursor = conn.cursor()

    for sheet in workbook.sheet_names:

        df = workbook.parse(sheet)

        current_topic = ""

        for column in df.columns:

            learning_type = str(column).strip()

            if learning_type == "":
                continue

            for value in df[column]:

                if pd.isna(value):
                    continue

                text = str(value).strip()

                if text == "":
                    continue

                # Pink headings become topics
                if learning_type.lower() == "modules":

                    current_topic = text
                    continue

                # Does this task already exist?
                cursor.execute(
                    """
                    SELECT id
                    FROM curriculum
                    WHERE module=?
                    AND learning_type=?
                    AND topic=?
                    AND task=?
                    """,
                    (
                        sheet,
                        learning_type,
                        current_topic,
                        text
                    )
                )

                existing = cursor.fetchone()

                # Skip if already imported
                if existing:

                    continue

                # Otherwise insert new task
                cursor.execute(
                    """
                    INSERT INTO curriculum
                    (
                        module,
                        learning_type,
                        topic,
                        task,
                        completed
                    )
                    VALUES (?, ?, ?, ?, 0)
                    """,
                    (
                        sheet,
                        learning_type,
                        current_topic,
                        text
                    )
                )

    conn.commit()
    conn.close()