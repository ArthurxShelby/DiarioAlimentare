import streamlit.components.v1 as components

html_code = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>React Artifact</title>
  <style>
    *,:after,:before {
      box-sizing: border-box;
      border: 0 solid #e5e7eb;
    }
  </style>
</head>
<body>
  <div id="root"></div>
  <script type="module">
    // Il tuo codice JavaScript qui
  </script>
</body>
</html>
"""

components.html(html_code, height=800, scrolling=True)
