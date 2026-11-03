document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("form[data-confirm]").forEach(form => {
    form.addEventListener("submit", event => {
      if (!window.confirm(form.dataset.confirm || "ادامه می‌دهید؟")) event.preventDefault();
    });
  });
  document.querySelectorAll('input[type="number"]').forEach(input => {
    input.addEventListener("change", () => {
      if (input.min !== "" && Number(input.value) < Number(input.min)) input.value = input.min;
      if (input.max !== "" && Number(input.value) > Number(input.max)) input.value = input.max;
    });
  });
});
