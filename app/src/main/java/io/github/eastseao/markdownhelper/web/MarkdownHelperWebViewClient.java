/*#######################################################
 *
 *   Maintained 2017-2025 by Gregor Santner <gsantner AT mailbox DOT org>
 *   License of this file: Apache 2.0
 *     https://www.apache.org/licenses/LICENSE-2.0
 *
#########################################################*/
package io.github.eastseao.markdownhelper.web;

import android.app.Activity;
import android.content.Context;
import android.webkit.WebView;

import io.github.eastseao.markdownhelper.activity.DocumentActivity;
import io.github.eastseao.markdownhelper.model.AppSettings;
import io.github.eastseao.markdownhelper.util.MarkdownHelperContextUtils;
import net.gsantner.opoc.web.GsWebViewClient;

import java.io.File;
import java.net.URLDecoder;

public class MarkdownHelperWebViewClient extends GsWebViewClient {
    protected final Activity _activity;

    public MarkdownHelperWebViewClient(final WebView webView, final Activity activity) {
        super(webView);
        _activity = activity;
    }

    @Override
    public boolean shouldOverrideUrlLoading(WebView view, String url) {
        try {
            Context context = view.getContext();

            if (url.equals("about:blank")) {
                view.reload();
                return true;
            }
            if (url.startsWith("file:///android_asset/")) {
                return false;
            } else if (url.startsWith("file://")) {
                MarkdownHelperContextUtils su = new MarkdownHelperContextUtils(view.getContext());
                File file = new File(URLDecoder.decode(url.replace("file://", "").replace("+", "%2B")));
                for (String str : new String[]{file.getAbsolutePath(), file.getAbsolutePath().replaceFirst("[#].*$", ""), file.getAbsolutePath() + ".md", file.getAbsolutePath() + ".txt"}) {
                    File f = new File(str);
                    if (f.exists()) {
                        file = f;
                        break;
                    }
                }
                DocumentActivity.launch(_activity, file, null, null);
            } else {
                MarkdownHelperContextUtils su = new MarkdownHelperContextUtils(_activity);
                AppSettings settings = AppSettings.get(_activity);
                if (!settings.isOpenLinksWithChromeCustomTabs() || (settings.isOpenLinksWithChromeCustomTabs() && !su.openWebpageInChromeCustomTab(context, url))) {
                    su.openWebpageInExternalBrowser(context, url);
                    return true;
                }
            }
        } catch (Exception ignored) {
        }
        return true;
    }
}
