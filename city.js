// Выбор города через ?setcity=<code>. Выбранный город запоминается в
// localStorage и показывается на всех страницах.
(function () {
  var CITIES = {
    almaty: "Алматы",
    astana: "Астана",
    shymkent: "Шымкент",
    karaganda: "Караганда",
    aktobe: "Актобе",
  };
  var DEFAULT_CITY = "almaty";
  var KEY = "city";

  var city = null;
  try {
    var param = new URLSearchParams(location.search).get("setcity");
    if (param) {
      param = param.toLowerCase();
      if (CITIES[param]) {
        city = param;
        localStorage.setItem(KEY, city);
      }
    }
    if (!city) city = localStorage.getItem(KEY);
  } catch (e) {}
  if (!CITIES[city]) city = DEFAULT_CITY;

  document.documentElement.dataset.city = city;
  function render() {
    document.querySelectorAll("[data-city-name]").forEach(function (el) {
      el.textContent = CITIES[city];
    });
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", render);
  } else {
    render();
  }
})();
