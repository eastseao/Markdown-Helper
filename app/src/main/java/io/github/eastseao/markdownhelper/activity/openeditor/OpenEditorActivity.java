/*#######################################################
 *
 *   Maintained 2017-2025 by Gregor Santner <gsantner AT mailbox DOT org>
 *   License of this file: Apache 2.0
 *     https://www.apache.org/licenses/LICENSE-2.0
 *
#########################################################*/
package io.github.eastseao.markdownhelper.activity.openeditor;

import android.content.Intent;
import android.os.Bundle;

import androidx.annotation.Nullable;

import io.github.eastseao.markdownhelper.activity.MarkdownHelperBaseActivity;
import io.github.eastseao.markdownhelper.activity.StoragePermissionActivity;
import io.github.eastseao.markdownhelper.model.Document;

import java.io.File;

public class OpenEditorActivity extends MarkdownHelperBaseActivity {

    @Override
    protected void onCreate(@Nullable final Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        StoragePermissionActivity.requestPermissions(this);
    }

    protected void openEditorForFile(final File file, final Integer line) {
        final Intent openIntent = new Intent(getApplicationContext(), OpenFromShortcutOrWidgetActivity.class)
                .setAction(Intent.ACTION_EDIT)
                .putExtra(Document.EXTRA_FILE, file);

        if (line != null) {
            openIntent.putExtra(Document.EXTRA_FILE_LINE_NUMBER, line);
        }

        _cu.animateToActivity(this, openIntent, true, 1);
    }
}
