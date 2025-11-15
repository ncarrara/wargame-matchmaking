import pandas as pd
import streamlit

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


@streamlit.cache_resource
def parse_com_faq() -> pd.DataFrame:
    import pandas as pd

    sheet_id = "1T34wopc3D0Iy-rrQ2N__et9w9mG8exuHf6BkJQ92yl0"
    gid = "1630105082"

    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

    df = pd.read_csv(url)
    return df


if __name__ == "__main__":
    parse_com_faq()