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

import android.content.Context;
import android.util.AttributeSet;
import android.view.View;

import androidx.annotation.NonNull;
import androidx.preference.PreferenceCategory;
import androidx.preference.PreferenceViewHolder;

/**
 * A {@link PreferenceCategory} whose header row can be tapped to collapse/expand its children.
 *
 * Needed because the "More" page carries 80+ settings and androidx.preference has no collapsible
 * category, so a plain category can only ever render as one long wall of rows. Every group here
 * starts collapsed, so the page opens as a short list of headings.
 *
 * The behaviour below was checked against the actual androidx.preference 1.2.0 bytecode rather
 * than assumed, because two details are non-obvious:
 *
 *   - {@code PreferenceCategory.isEnabled()} is hard-coded to return false, and
 *     {@code Preference.onBindViewHolder} only installs the framework click listener when the
 *     preference is enabled. Overriding isEnabled() to true is therefore what makes the header
 *     row tappable at all.
 *   - {@code PreferenceCategory.onBindViewHolder} does not touch the item view's click listener,
 *     so installing our own listener after super.onBindViewHolder() is safe and is the primary
 *     click path (the framework path via onClick() is kept as a fallback).
 *
 * Hiding is done with {@link androidx.preference.Preference#setVisible(boolean)} on the direct
 * children. That hides a child's whole subtree as well, because
 * {@code PreferenceGroupAdapter.createVisiblePreferencesList} skips invisible preferences and only
 * recurses into a group that is itself visible - which is what makes nested sub categories
 * (colour scheme, syntax highlighting, per-format blocks, ...) fold away with their parent group.
 */
public class ExpandablePreferenceCategory extends PreferenceCategory {

    private boolean _expanded = false;
    private CharSequence _baseTitle;

    public ExpandablePreferenceCategory(Context context) {
        super(context);
    }

    public ExpandablePreferenceCategory(Context context, AttributeSet attrs) {
        super(context, attrs);
    }

    public ExpandablePreferenceCategory(Context context, AttributeSet attrs, int defStyleAttr) {
        super(context, attrs, defStyleAttr);
    }

    public ExpandablePreferenceCategory(Context context, AttributeSet attrs, int defStyleAttr, int defStyleRes) {
        super(context, attrs, defStyleAttr, defStyleRes);
    }

    /**
     * PreferenceCategory pins this to false. Reporting true is what lets the framework treat the
     * header as an interactive row; the real "enabled" flag used for dependent preferences is a
     * separate field in PreferenceGroup and stays untouched.
     */
    @Override
    public boolean isEnabled() {
        return true;
    }

    /** Framework click path. */
    @Override
    protected void onClick() {
        setExpandedState(!_expanded);
    }

    @Override
    public void onAttached() {
        super.onAttached();
        rememberBaseTitle();
        applyChildVisibility();
    }

    @Override
    public void onBindViewHolder(@NonNull PreferenceViewHolder holder) {
        super.onBindViewHolder(holder);
        rememberBaseTitle();
        final View itemView = holder.itemView;
        itemView.setClickable(true);
        itemView.setOnClickListener(view -> setExpandedState(!_expanded));
    }

    public boolean isExpandedState() {
        return _expanded;
    }

    public void setExpandedState(boolean expanded) {
        if (_expanded == expanded) {
            return;
        }
        _expanded = expanded;
        applyChildVisibility();
        updateIndicator();
        notifyChanged();
    }

    private void applyChildVisibility() {
        for (int i = 0; i < getPreferenceCount(); i++) {
            getPreference(i).setVisible(_expanded);
        }
    }

    private void rememberBaseTitle() {
        if (_baseTitle == null) {
            _baseTitle = getTitle();
        }
    }

    private void updateIndicator() {
        if (_baseTitle != null) {
            // U+25B8 / U+25BE (small solid triangles). Language independent on purpose, so the
            // expand/collapse affordance needs no new translation in any of the locales.
            setTitle((_expanded ? "\u25BE  " : "\u25B8  ") + _baseTitle);
        }
    }
}
