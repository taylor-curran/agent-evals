✗ python match_issues.py
# 18035
TITLE : ModuleNotFoundError: No module named 'referencing'
STATE : closed
REASON: completed
BODY  :
 ### Bug summary

In the process of upgrading a project from Prefect V2 to V3. On running prefect server database upgrade I get the following:

Traceback (most recent call last):
  File "<redacted>\.pyenv\pyenv-win\versions\3.10.11\lib\runpy.py", line 196, in _run_module_as_main
    return _run_code(code, main_globals, None,
  File "<redacted>\.pyenv\pyenv-win\versions\3.10.11\lib\runpy.py", line 86, in _run_code
    exec(code, run_globals)
  File "<redacted>\.venv\Scripts\prefect.exe\__main__.py", line 4, in <module>
    from prefect.cli import app
  File "<redacted>\.venv\lib\site-packages\prefect\cli\__init__.py", line 24, in <module>
    import prefect.cli.server
  File "<redacted>\.venv\lib\site-packages\prefect\cli\server.py", line 32, in <module>
    from prefect.server.services.base import Service
  File "<redacted>\.venv\lib\site-packages\prefect\server\__init__.py", line 1, in <module>
    from . import models, orchestration, schemas, services
  File "<redacted>\.venv\lib\site-packages\prefect\server\models\__init__.py", line 1, in <module>
    from . import (
  File "<redacted>\.venv\lib\site-packages\prefect\server\models\artifacts.py", line 9, in <module>
    from prefect.server.database import PrefectDBInterface, db_injector, orm_models
  File "<redacted>\.venv\lib\site-packages\prefect\server\database\__init__.py", line 6, in <module>
    from prefect.server.database.interface import PrefectDBInterface
  File "<redacted>\.venv\lib\site-packages\prefect\server\database\interface.py", line 9, in <module>
    from prefect.server.database import orm_models
  File "<redacted>\.venv\lib\site-packages\prefect\server\database\orm_models.py", line 26, in <module>
    from prefect.server.events.actions import ServerActionTypes
  File "<redacted>\.venv\lib\site-packages\prefect\server\events\actions.py", line 86, in <module>
    from prefect.utilities.schema_tools.hydration import (
  File "<redacted>\.venv\lib\site-packages\prefect\utilities\schema_tools\__init__.py", line 2, in <module>
    from .validation import (
  File "<redacted>\.venv\lib\site-packages\prefect\utilities\schema_tools\validation.py", line 9, in <module>
    from referencing.jsonschema import ObjectSchema, Schema
ModuleNotFoundError: No module named 'referencing'


Appears to be related to https://github.com/PrefectHQ/prefect/pull/16298, where a dependency on the referencing package was added, however it does not appear to be included in the Prefect dependencies.

Adding the dependency to my own project resolves the issue as a workaround.

### Version info

Text
Version:             3.4.1
API version:         0.8.4
Python version:      3.10.11
Git commit:          b47ad8e1
Built:               Thu, May 08, 2025 08:42 PM
OS/Arch:             win32/AMD64
Profile:             local
Server type:         ephemeral
Pydantic version:    2.11.4
Server:
  Database:          sqlite
  SQLite version:    3.40.1
Integrations:
  prefect-snowflake: 0.28.4


### Additional context

_No response_
--------------------------------------------------------------------------------
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
COMMENT ID: 2877530003
USER: desertaxle
CREATED: 2025-05-13T18:18:59Z
UPDATED: 2025-05-13T18:18:59Z
AUTHOR ASSOCIATION: MEMBER
BODY:
 Thanks for the issue @Daveography! referencing is a dependency of jsonschema, which is a dependency of prefect, so I'm surprised that referencing wasn't installed when you installed prefect. Could you share how you installed prefect so I can see if I can recreate the issue?
REACTIONS: 0
NODE ID: IC_kwDOCEwExM6rg5-T
ISSUE URL: https://api.github.com/repos/PrefectHQ/prefect/issues/18035
URL: https://github.com/PrefectHQ/prefect/issues/18035#issuecomment-2877530003
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
COMMENT ID: 2877553905
USER: Daveography
CREATED: 2025-05-13T18:27:05Z
UPDATED: 2025-05-13T18:27:05Z
AUTHOR ASSOCIATION: NONE
BODY:
 > Thanks for the issue [@Daveography](https://github.com/Daveography)! referencing is a dependency of jsonschema, which is a dependency of prefect, so I'm surprised that referencing wasn't installed when you installed prefect. Could you share how you installed prefect so I can see if I can recreate the issue?

I previously had Prefect 2.16.5 installed, which at the time installed jsonschema 4.17.3. jsonschema was not upgraded on updating prefect to 3.4.1. It looks like the referencing dependency was added just after, in [4.18.0](https://github.com/python-jsonschema/jsonschema/blob/main/CHANGELOG.rst#v4180).
REACTIONS: 0
NODE ID: IC_kwDOCEwExM6rg_zx
ISSUE URL: https://api.github.com/repos/PrefectHQ/prefect/issues/18035
URL: https://github.com/PrefectHQ/prefect/issues/18035#issuecomment-2877553905
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
COMMENT ID: 2877614720
USER: Daveography
CREATED: 2025-05-13T18:52:05Z
UPDATED: 2025-05-13T18:52:05Z
AUTHOR ASSOCIATION: NONE
BODY:
 With that in mind, updating jsonschema to >=4.18.0 in my project was also an effective workaround.
REACTIONS: 0
NODE ID: IC_kwDOCEwExM6rhOqA
ISSUE URL: https://api.github.com/repos/PrefectHQ/prefect/issues/18035
URL: https://github.com/PrefectHQ/prefect/issues/18035#issuecomment-2877614720
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
COMMENT ID: 2877921254
USER: zzstoatzz
CREATED: 2025-05-13T20:55:30Z
UPDATED: 2025-05-13T20:55:30Z
AUTHOR ASSOCIATION: COLLABORATOR
BODY:
 hi @Daveography - we've updated the lower bound on jsonschema so that people should no longer encounter this - thanks!
REACTIONS: 1
NODE ID: IC_kwDOCEwExM6riZfm
ISSUE URL: https://api.github.com/repos/PrefectHQ/prefect/issues/18035
URL: https://github.com/PrefectHQ/prefect/issues/18035#issuecomment-2877921254
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
********************************************************************************
EVENT ID: 17640202170.0
EVENT   : labeled
CREATED : 2025-05-13T17:52:09Z
ACTOR   : Daveography
COMMIT  : nan
COMMIT URL: nan
NODE ID : LE_lADOCEwExM62cFa6zwAAAAQbcB-6
PR #    : nan
PR URL  : nan
LABEL   : bug
SOURCE  : nan
APP     : nan
URL     : https://api.github.com/repos/PrefectHQ/prefect/issues/events/17640202170
********************************************************************************
********************************************************************************
EVENT ID: 2877530003.0
EVENT   : commented
CREATED : 2025-05-13T18:18:59Z
ACTOR   : desertaxle
COMMIT  : nan
COMMIT URL: nan
NODE ID : IC_kwDOCEwExM6rg5-T
PR #    : nan
PR URL  : nan
LABEL   : nan
SOURCE  : nan
APP     : nan
URL     : https://api.github.com/repos/PrefectHQ/prefect/issues/comments/2877530003
********************************************************************************
********************************************************************************
EVENT ID: 17640543087.0
EVENT   : mentioned
CREATED : 2025-05-13T18:19:00Z
ACTOR   : Daveography
COMMIT  : nan
COMMIT URL: nan
NODE ID : MEE_lADOCEwExM62cFa6zwAAAAQbdVNv
PR #    : nan
PR URL  : nan
LABEL   : nan
SOURCE  : nan
APP     : nan
URL     : https://api.github.com/repos/PrefectHQ/prefect/issues/events/17640543087
********************************************************************************
********************************************************************************
EVENT ID: 17640543111.0
EVENT   : subscribed
CREATED : 2025-05-13T18:19:00Z
ACTOR   : Daveography
COMMIT  : nan
COMMIT URL: nan
NODE ID : SE_lADOCEwExM62cFa6zwAAAAQbdVOH
PR #    : nan
PR URL  : nan
LABEL   : nan
SOURCE  : nan
APP     : nan
URL     : https://api.github.com/repos/PrefectHQ/prefect/issues/events/17640543111
********************************************************************************
********************************************************************************
EVENT ID: 2877553905.0
EVENT   : commented
CREATED : 2025-05-13T18:27:05Z
ACTOR   : Daveography
COMMIT  : nan
COMMIT URL: nan
NODE ID : IC_kwDOCEwExM6rg_zx
PR #    : nan
PR URL  : nan
LABEL   : nan
SOURCE  : nan
APP     : nan
URL     : https://api.github.com/repos/PrefectHQ/prefect/issues/comments/2877553905
********************************************************************************
********************************************************************************
EVENT ID: 2877614720.0
EVENT   : commented
CREATED : 2025-05-13T18:52:05Z
ACTOR   : Daveography
COMMIT  : nan
COMMIT URL: nan
NODE ID : IC_kwDOCEwExM6rhOqA
PR #    : nan
PR URL  : nan
LABEL   : nan
SOURCE  : nan
APP     : nan
URL     : https://api.github.com/repos/PrefectHQ/prefect/issues/comments/2877614720
********************************************************************************
********************************************************************************
EVENT ID: nan
EVENT   : cross-referenced
CREATED : 2025-05-13T19:20:05Z
ACTOR   : zzstoatzz
COMMIT  : nan
COMMIT URL: nan
NODE ID : nan
PR #    : nan
PR URL  : nan
LABEL   : nan
SOURCE  : issue
APP     : nan
URL     : nan
********************************************************************************
********************************************************************************
EVENT ID: 17642536564.0
EVENT   : closed
CREATED : 2025-05-13T20:54:59Z
ACTOR   : zzstoatzz
COMMIT  : nan
COMMIT URL: nan
NODE ID : CE_lADOCEwExM62cFa6zwAAAAQbk750
PR #    : nan
PR URL  : nan
LABEL   : nan
SOURCE  : nan
APP     : nan
URL     : https://api.github.com/repos/PrefectHQ/prefect/issues/events/17642536564
********************************************************************************
********************************************************************************
EVENT ID: 2877921254.0
EVENT   : commented
CREATED : 2025-05-13T20:55:30Z
ACTOR   : zzstoatzz
COMMIT  : nan
COMMIT URL: nan
NODE ID : IC_kwDOCEwExM6riZfm
PR #    : nan
PR URL  : nan
LABEL   : nan
SOURCE  : nan
APP     : nan
URL     : https://api.github.com/repos/PrefectHQ/prefect/issues/comments/2877921254
********************************************************************************
********************************************************************************
EVENT ID: 17642542356.0
EVENT   : mentioned
CREATED : 2025-05-13T20:55:31Z
ACTOR   : Daveography
COMMIT  : nan
COMMIT URL: nan
NODE ID : MEE_lADOCEwExM62cFa6zwAAAAQbk9UU
PR #    : nan
PR URL  : nan
LABEL   : nan
SOURCE  : nan
APP     : nan
URL     : https://api.github.com/repos/PrefectHQ/prefect/issues/events/17642542356
********************************************************************************
********************************************************************************
EVENT ID: 17642542370.0
EVENT   : subscribed
CREATED : 2025-05-13T20:55:31Z
ACTOR   : Daveography
COMMIT  : nan
COMMIT URL: nan
NODE ID : SE_lADOCEwExM62cFa6zwAAAAQbk9Ui
PR #    : nan
PR URL  : nan
LABEL   : nan
SOURCE  : nan
APP     : nan
URL     : https://api.github.com/repos/PrefectHQ/prefect/issues/events/17642542370
********************************************************************************
- ~ -- ~ -- ~ -- ~ -- ~ -- ~ -- ~ -- ~ -- ~ -- ~ -- ~ -- ~ -- ~ -- ~ -- ~ -- ~ -- ~ -- ~ -- ~ -- ~ -- ~ -- ~ -- ~ -- ~ -- ~ -- ~ -- ~ -- ~ -- ~ -- ~ -- ~ -- ~ -- ~ -- ~ -- ~ -- ~ -- ~ -- ~ -- ~ -- ~ -