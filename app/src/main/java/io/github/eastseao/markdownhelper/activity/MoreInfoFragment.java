/*#######################################################
 *
 *   Maintained 2017-2025 by Gregor Santner <gsantner AT mailbox DOT org>
 *
 *   License of this file: Apache 2.0
 *     https://www.apache.org/licenses/LICENSE-2.0
 *     https://github.com/gsantner/opoc/#licensing
 *
#########################################################*/

package io.github.eastseao.markdownhelper.activity;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.net.Uri;
import android.text.InputType;

import androidx.preference.EditTextPreference;
import androidx.preference.Preference;
import androidx.preference.PreferenceGroup;

import io.github.eastseao.markdownhelper.R;
import io.github.eastseao.markdownhelper.model.AppSettings;
import net.gsantner.opoc.format.GsSimpleMarkdownParser;
import net.gsantner.opoc.frontend.base.GsPreferenceFragmentBase;

import java.io.IOException;
import java.util.Locale;

public class MoreInfoFragment extends GsPreferenceFragmentBase<AppSettings> {
    public static final String TAG = "MoreInfoFragment";

    public static MoreInfoFragment newInstance() {
        return new MoreInfoFragment();
    }

    @Override
    public int getPreferenceResourceForInflation() {
        return R.xml.prefactions__more_information;
    }

    @Override
    public String getFragmentTag() {
        return TAG;
    }

    @Override
    protected AppSettings getAppSettings(Context context) {
        return AppSettings.get(context);
    }

    @Override
    public boolean isDividerVisible() {
        return true;
    }

    @Override
    @SuppressWarnings({"ConstantConditions", "ConstantIfStatement", "StatementWithEmptyBody"})
    public Boolean onPreferenceClicked(Preference preference, String key, int keyResId) {
        if (isAdded() && preference.hasKey()) {
            switch (keyResId) {
                case R.string.pref_key__more_info__app: {
                    _cu.openWebpageInExternalBrowser(getContext(), getString(R.string.app_web_url));
                    return true;
                }
            }
        }
        return null;
    }

    @Override
    protected boolean isAllowedToTint(Preference pref) {
        return !getString(R.string.pref_key__more_info__app).equals(pref.getKey());
    }

    @Override
    public synchronized void doUpdatePreferences() {
        super.doUpdatePreferences();
        Context context = getContext();
        if (context == null) {
            return;
        }
        final Locale locale = Locale.getDefault();
        Preference pref;
        // Basic app info
        if ((pref = findPreference(R.string.pref_key__more_info__app)) != null && pref.getSummary() == null) {
            pref.setIcon(R.drawable.ic_launcher);
            pref.setSummary(String.format(locale, "%s\nVersion v%s (%d)", _cu.getAppIdFlavorSpecific(context), _cu.getAppVersionName(context), _cu.bcint(context, "VERSION_CODE", 0)));
        }
        // The export settings are shown inline here (the "settings" sub page was flattened into
        // this screen), so their summaries have to be kept in sync on this screen as well.
        if ((pref = findPreference(R.string.pref_key__share_image_export_width)) != null) {
            pref.setSummary(_appSettings.getShareImageExportWidth() + " px");
            if (pref instanceof EditTextPreference) {
                ((EditTextPreference) pref).setOnBindEditTextListener(editText -> {
                    editText.setInputType(InputType.TYPE_CLASS_NUMBER);
                    editText.setSelection(editText.getText().length());
                });
            }
        }
    }
}
