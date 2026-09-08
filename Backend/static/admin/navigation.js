(() => {
    "use strict";

    const APP_GROUP_SELECTOR = 'div[x-data^="{navigationOpen"] > h2';

    const initializeAppToggle = () => {
        const navigation = document.querySelector("#nav-sidebar-apps");
        if (!navigation || navigation.querySelector("[data-admin-app-toggle]")) {
            return;
        }

        const appHeadings = () => [...navigation.querySelectorAll(APP_GROUP_SELECTOR)];
        if (appHeadings().length === 0) {
            return;
        }

        const wrapper = document.createElement("div");
        wrapper.className = "admin-app-toggle-wrap";
        wrapper.dataset.adminAppToggle = "";

        const button = document.createElement("button");
        button.className = "admin-app-toggle";
        button.type = "button";

        const icon = document.createElement("span");
        icon.className = "material-symbols-outlined";
        icon.setAttribute("aria-hidden", "true");

        const label = document.createElement("span");
        button.append(icon, label);
        wrapper.append(button);
        navigation.prepend(wrapper);

        const appList = (heading) => heading.parentElement.querySelector(":scope > ol");
        const isExpanded = (heading) => {
            const list = appList(heading);
            return Boolean(list && window.getComputedStyle(list).display !== "none");
        };

        const synchronizeButton = () => {
            const headings = appHeadings();
            const allExpanded = headings.length > 0 && headings.every(isExpanded);
            icon.textContent = allExpanded ? "unfold_less" : "unfold_more";
            label.textContent = allExpanded ? "Collapse all apps" : "Expand all apps";
            button.setAttribute("aria-expanded", String(allExpanded));
            button.title = label.textContent;
        };

        button.addEventListener("click", () => {
            const headings = appHeadings();
            const expand = headings.some((heading) => !isExpanded(heading));

            headings.forEach((heading) => {
                if (isExpanded(heading) !== expand) {
                    heading.click();
                }
            });

            window.requestAnimationFrame(synchronizeButton);
        });

        navigation.addEventListener("click", (event) => {
            if (event.target.closest(APP_GROUP_SELECTOR)) {
                window.requestAnimationFrame(synchronizeButton);
            }
        });

        synchronizeButton();
    };

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initializeAppToggle, {once: true});
    } else {
        initializeAppToggle();
    }

    document.addEventListener("htmx:afterSwap", initializeAppToggle);
})();
