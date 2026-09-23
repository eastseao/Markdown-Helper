/*#######################################################
 *
 *   Maintained 2018-2025 by Gregor Santner <gsantner AT mailbox DOT org>
 *   License of this file: Apache 2.0
 *     https://www.apache.org/licenses/LICENSE-2.0
 *
#########################################################*/
package io.github.eastseao.markdownhelper.format.keyvalue;

import io.github.eastseao.markdownhelper.format.plaintext.PlaintextTextConverter;

import java.io.File;
import java.util.Arrays;
import java.util.List;

@SuppressWarnings("WeakerAccess")
public class KeyValueTextConverter extends PlaintextTextConverter {
    private static final List<String> EXT = Arrays.asList(".yml", ".yaml", ".toml", ".vcf", ".ics", ".ini", ".json", ".zim");

    @Override
    protected boolean isFileOutOfThisFormat(final File file, final String name, final String ext) {
        return EXT.contains(ext);
    }
}
