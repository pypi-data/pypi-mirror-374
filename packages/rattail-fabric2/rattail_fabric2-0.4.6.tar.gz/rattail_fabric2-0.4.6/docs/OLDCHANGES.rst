
CHANGELOG
=========

NB. this file contains "old" release notes only.  for newer releases
see the `CHANGELOG.md` file in the source root folder.


0.3.6 (2024-05-31)
------------------

* Bump version to fix PyPI upload.


0.3.5 (2024-05-31)
------------------

* Fix command line args in scripts, per typer.


0.3.4 (2024-05-07)
------------------

* Fix shell when creating new linux user account.


0.3.3 (2023-09-25)
------------------

* Add separate functions for dump, restore of mysql DB.

* Preserve correct owner for ``.bashrc`` when configuring node.js.

* Move sql file to temp path when restoring postgres db.

* Add ``clang`` workaround for pythonz.

* Add ``mysql.get_version_string()`` convenience function.

* Add option to skip raw SQL file when dumping postgres DB.


0.3.2 (2023-06-10)
------------------

* Let caller override default ``fannie/config.php``.


0.3.1 (2023-06-10)
------------------

* Touch ``fannie.log`` when installing CORE Office.

* Add password support for ``make_normal_user()``.


0.3.0 (2023-06-08)
------------------

- OMG so many changes...just needed a fresh release.


0.2.4 (2020-09-25)
------------------

- Allow kwargs for template context when deploying sudoers file.
- Pass arbitrary kwargs along, for ``apt.install()``.
- Add ``method`` kwarg for ``python.install_pip()``.
- Require the 'rattail' package.
- Add ``mssql`` module for installing MS SQL Server ODBC driver.
- Add ``is_debian()`` convenience function.


0.2.3 (2020-09-08)
------------------

- Improve support for installing pip etc. on python3.


0.2.2 (2020-09-08)
------------------

- Include all "deploy" files within manifest.


0.2.1 (2020-09-08)
------------------

- OMG so many changes.  Just a "save point" more or less.


0.2.0 (2018-12-03)
------------------

- Initial release, somewhat forked from ``rattail-fabric`` package.
