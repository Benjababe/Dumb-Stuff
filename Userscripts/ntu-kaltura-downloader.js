// ==UserScript==
// @name         NTU Kaltura Downloader
// @namespace    https://greasyfork.org/en/users/86284-benjababe
// @version      1.1.6
// @description  Fuck kaltura. It's shit
// @author       Benjababe
// @license      MIT

// @match        https://ntulearn.ntu.edu.sg/webapps/*
// @match        https://ntulearnv.ntu.edu.sg/media/*
// @match        https://ntulearnv.ntu.edu.sg/playlist/dedicated/*

// @grant        none
// ==/UserScript==

// jshint esversion: 8
(function () {
    const partnerID = "117",
        sourceTemplate = `https://api.sg.kaltura.com/p/${partnerID}/sp/${partnerID}00/playManifest/entryId/%ENTRY_ID_HERE%/format/download/protocol/https/flavorParamIds/0`,
        entryPrefix = "/entry_id/";

    console.log(sourceTemplate);

    window.onload = () => {
        // regular blackboard page with embedded player
        if (location.pathname.indexOf("/webapps/blackboard/") == 0) {
            genBlackBoard();
        }

        // kaltura single media
        if (location.pathname.includes("/media/t/")) {
            genKPage(false);
        }

        // kaltura playlist
        if (location.pathname.includes("/playlist/dedicated/")) {
            genKPage(true);
        }
    };

    let genBlackBoard = () => {
        console.log("NTU Kaltura Downloader running...");

        genEmbeddedVideos();
        genLinks();
    };


    // generates download button for embedded kaltura videos in blackboard page (eg. CZ1106)
    let genEmbeddedVideos = () => {
        let iframes = Array.from(document.getElementsByTagName("iframe"));
        iframes.forEach((iframe) => {
            let src = iframe.src,
                sIndex = src.indexOf(entryPrefix);

            //stops if it isn't a kultura video iframe
            if (sIndex != -1) {
                let eidIndex = src.indexOf(entryPrefix) + entryPrefix.length;
                src = src.substring(eidIndex);
                let entryID = src.substring(0, src.indexOf("/")),
                    sourceURL = sourceTemplate.replace("%ENTRY_ID_HERE%", entryID);

                appendDownloadButton(iframe, sourceURL);
            }
        });
    };

    // generated download button for <a> tags to kaltura videos in blackboard page (eg. CZ2002)
    let genLinks = () => {
        let links = Array.from(document.querySelectorAll("a[target]"));
        links.forEach((link) => {
            if (link.href.indexOf("https://api.sg.kaltura.com") == 0) {
                let url = link.href,
                    entryID = url.split("entry_id=")[1],
                    sourceURL = sourceTemplate.replace("%ENTRY_ID_HERE%", entryID);

                appendDownloadButton(link, sourceURL);
            }
        });
    };


    // generates download button in the kaltura media gallery (eg. CZ2005)
    let genKPage = (playlist = false) => {
        let sourceURL = getSourceURL(playlist);
        listenDOM(playlist);
    };


    // returns video source URL using entry ID in current URL
    let getSourceURL = (playlist = false) => {
        let path = location.pathname, entryID, sourceURL;
        let pathSpl = path.replace("/media/t/", "").split("/");

        if (playlist) {
            entryID = pathSpl[pathSpl.length - 1];
        }

        else {
            entryID = pathSpl[0];
        }

        sourceURL = sourceTemplate.replace("%ENTRY_ID_HERE%", entryID);
        return sourceURL;
    };


    // appends download button with sourceURL to whatever element is passed through sibling argument
    let appendDownloadButton = (sibling, sourceURL) => {
        let dlBtn = document.createElement("button");
        dlBtn.innerText = "Download";
        dlBtn.style.position = "absolute";
        dlBtn.style.userSelect = "none";
        dlBtn.style.marginLeft = "10px";
        dlBtn.onclick = (e) => { window.location.href = sourceURL; e.target.blur(); };

        sibling.parentNode.appendChild(dlBtn);
    };


    // larger video should have a poster attribute with entry_id
    let getLargerVidEntryID = (kVideo) => {
        let posterURL = kVideo.getAttribute("poster"),
            posterRegex = /entry_id\/([\w]+)\//,
            match = posterURL.match(posterRegex);

        return match[1];
    };


    // appends download to action list when it is detected in MutationObserver
    // whole page doesn't load in at once in this scenario
    let listenDOM = (playlist = false) => {
        let observer = new window.MutationObserver(function (mutations, observer) {
            let ul = document.querySelector("ul#entryActionsMenu");

            // only appends when the "ACTIONS" dropdown list is loaded in
            if (ul != undefined) {
                let btnDl = document.querySelectorAll(".btn-dl");

                // remove previously added download buttons
                if (btnDl != undefined) {
                    for (let i = 0; i < btnDl.length; i++) {
                        btnDl[i].remove();
                    }
                }

                // needs to look into inner iframe context to search for video element
                let kplayerIFrame = document.querySelector("#kplayer_ifp"),
                    kplayerIFrameDOM = kplayerIFrame.contentWindow.document.body,
                    kVideos = Array.from(kplayerIFrameDOM.getElementsByTagName("video"));

                // for each video, insert a download button
                for (let i = 0; i < kVideos.length; i++) {
                    let kVideo = kVideos[i],
                        sourceURL = "",
                        entryID = 0;

                    // this should be the smaller video by default
                    if (kVideo.hasAttribute("kentryid")) {
                        entryID = kVideo.getAttribute("kentryid");
                    }

                    // this should be the bigger video by default
                    else {
                        entryID = getLargerVidEntryID(kVideo);
                    }

                    sourceURL = sourceTemplate.replace("%ENTRY_ID_HERE%", entryID);

                    // inserts download button into dropdown list
                    let li = document.createElement("li"),
                        a = document.createElement("a"),
                        span = document.createElement("span");

                    span.innerText = `Download Source ${i + 1}`;
                    a.appendChild(span);
                    a.href = sourceURL;
                    li.appendChild(a);
                    li.className = "btn-dl";
                    li.setAttribute("role", "presentation");
                    ul.appendChild(li);
                }
            }
        });

        observer.observe(document, {
            subtree: true,
            attributes: true
        });
    };

})();









