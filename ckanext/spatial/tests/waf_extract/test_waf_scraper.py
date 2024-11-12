import os

from ckanext.spatial.harvesters.waf import _extract_waf

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_DIR = os.path.join(TEST_DIR, "html_files")

def test_extract_iis(httpserver):

    # feed http response with these static html content
    with \
            open(f"{HTML_DIR}/iis-folder.html", "r") as iis_folder, \
            open(f"{HTML_DIR}/nginx-folder.html", "r") as nginx_folder, \
            open(f"{HTML_DIR}/apache-folder.html", "r") as apache_folder, \
            open(f"{HTML_DIR}/iis-subfolder.html", "r") as iis_subfolder, \
            open(f"{HTML_DIR}/nginx-subfolder.html", "r") as nginx_subfolder, \
            open(f"{HTML_DIR}/apache-subfolder.html", "r") as apache_subfolder:
        iis_folder_content = iis_folder.read()
        nginx_folder_content = nginx_folder.read()
        apache_folder_content = apache_folder.read()
        iis_subfolder_content = iis_subfolder.read()
        nginx_subfolder_content = nginx_subfolder.read()
        apache_subfolder_content = apache_subfolder.read()

    # feed static content when it traverses the subfolder
    httpserver.expect_request("/iis-folder/subfolder/").respond_with_data(iis_subfolder_content)
    httpserver.expect_request("/nginx-folder/subfolder/").respond_with_data(nginx_subfolder_content)
    httpserver.expect_request("/apache-folder/subfolder/").respond_with_data(apache_subfolder_content)

    # let it scape, traverse and extract the content
    iis_results = _extract_waf(
        iis_folder_content,
        httpserver.url_for("/iis-folder/"),
        "iis"
    )

    nginx_results = _extract_waf(
        nginx_folder_content,
        httpserver.url_for("/nginx-folder/"),
        "nginx"
    )

    apache_results = _extract_waf(
        apache_folder_content,
        httpserver.url_for("/apache-folder/"),
        "apache"
    )

    records_expected = [('record-1.xml', '2024-11-07 15:00:00'), ('record-2.xml', '2024-11-07 16:59:00')]

    assert records_expected == sorted([(os.path.basename(r[0]), r[1]) for r in iis_results])
    assert records_expected == sorted([(os.path.basename(r[0]), r[1]) for r in nginx_results])
    assert records_expected == sorted([(os.path.basename(r[0]), r[1]) for r in apache_results])
