
package com.alvis.media.utility;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.HexFormat;


/**
 *@author 奇趣
 */
public class Md5Util {

    private static final Logger logger = LoggerFactory.getLogger(Md5Util.class);

    public static String encode(String pwd) {
        String hash = null;
        try {
            hash = HexFormat.of().withUpperCase().formatHex(
                    MessageDigest.getInstance("MD5").digest(pwd.getBytes(StandardCharsets.UTF_8)));
        } catch (NoSuchAlgorithmException e) {
            logger.error(e.getMessage(), e);
        }
        return hash;
    }
}
