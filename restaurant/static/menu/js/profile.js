document.addEventListener("DOMContentLoaded", function () {
    const links = document.querySelectorAll(".profile-menu a");
    const sections = document.querySelectorAll(".profile-section");

    function showSection(id) {
        if (!id.startsWith("#")) return;
        sections.forEach(section => section.classList.remove("active"));
        const target = document.querySelector(id);
        if (target) target.classList.add("active");
    }

    // default section
    if (window.location.hash && window.location.hash.startsWith("#")) showSection(window.location.hash);
    else showSection("#profile-info");

    links.forEach(link => {
        const id = link.getAttribute("href");
        if (!id.startsWith("#")) return;
        link.addEventListener("click", function (e) {
            e.preventDefault();
            history.pushState(null, "", id);
            showSection(id);
        });
    });
});

function enableEditProfile() {
    document.getElementById("profile-view").style.display="none";
    document.getElementById("profile-edit").style.display="block";
}

function cancelEditProfile() {
    document.getElementById("profile-edit").style.display="none";
    document.getElementById("profile-view").style.display="block";
}
