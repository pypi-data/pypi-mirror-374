#!/bin/sh -e

cd ${envroot}

export RATTAIL_CONFIG_FILES=${overnight_conf}
# nb. avoid rich-formatted traceback here since it's so "noisy"
export _TYPER_STANDARD_TRACEBACK=1

bin/rattail --no-versioning overnight -k ${automation.lower()} <%text>\</%text>
        % if email_key is not Undefined and email_key:
        --email-key '${email_key}' <%text>\</%text>
        % endif
        --email-if-empty <%text>\</%text>
        --no-wait
