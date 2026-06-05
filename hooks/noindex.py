NOINDEX_META = """
  <meta name="robots" content="noindex,nofollow,noarchive,nosnippet">
  <meta name="googlebot" content="noindex,nofollow,noarchive,nosnippet">
  <meta name="bingbot" content="noindex,nofollow,noarchive,nosnippet">
"""

def on_post_page(output, page, config):
    if '<meta name="robots"' in output:
        return output

    if "<head>" in output:
        return output.replace("<head>", "<head>" + NOINDEX_META, 1)

    return output
