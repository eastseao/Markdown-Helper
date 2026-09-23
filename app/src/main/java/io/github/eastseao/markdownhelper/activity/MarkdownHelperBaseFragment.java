package io.github.eastseao.markdownhelper.activity;

import android.content.Context;

import io.github.eastseao.markdownhelper.model.AppSettings;
import io.github.eastseao.markdownhelper.util.MarkdownHelperContextUtils;
import net.gsantner.opoc.frontend.base.GsFragmentBase;

public abstract class MarkdownHelperBaseFragment extends GsFragmentBase<AppSettings, MarkdownHelperContextUtils> {
    @Override
    public AppSettings createAppSettingsInstance(Context context) {
        return AppSettings.get(context);
    }

    @Override
    public MarkdownHelperContextUtils createContextUtilsInstance(Context context) {
        return new MarkdownHelperContextUtils(context);
    }
}
