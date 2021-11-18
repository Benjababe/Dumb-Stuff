// ==UserScript==
// @name         Chin Fast Image Downloader
// @namespace    https://greasyfork.org/en/users/86284-benjababe
// @version      1.04
// @description  One click to download current hovered image/webmeme
// @author       Benjababe
// @license      MIT

// @match        https://boards.4channel.org/*
// @match        https://arch.b4k.co/*
// @match        https://archived.moe/*
// @match        https://archive.nyafuu.org/*
// @match        https://archive.wakarimasen.moe/*
// @match        https://desuarchive.org/*
// @match        https://warosu.org/*

// @grant        GM_download
// ==/UserScript==

// jshint esversion: 6

(function () {
    'use strict';

    const HOTKEY = "Pause";

    document.onkeydown = (e) => {
        // key can be whatever you want, I choose pause as it's what I bound my mouse side keys to
        if (e.code === HOTKEY) {
            // get all elements hovered
            let els = document.querySelectorAll(":hover");
            els.forEach((el) => {
                // only download for images
                if (el.tagName.toLowerCase() === "img") {
                    // link to original image/webmeme usually is the parent <a> element
                    let parent = el.parentNode,
                        url = parent.href,
                        filename = HDFilenameFromURL(url);
                    GM_download(url, filename);
                }
            });
        }
    }

    // eg. ".../1622014662736s.jpg -> 1622014662736.jpg"
    let HDFilenameFromURL = (url) => {
        let SDFilename = url.split("/").pop();
        SDFilename = SDFilename.split(".");

        if (SDFilename[0][SDFilename[0].length - 1] == "s") {
            SDFilename[0] = SDFilename[0].slice(0, -1);
        }

        return SDFilename.join(".");
    }
})();