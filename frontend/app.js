const form = document.getElementById('price-form');
const result = document.getElementById('result');

form.addEventListener('submit', async (event) => {
  event.preventDefault();

  const area = document.getElementById('area').value.trim();
  const bedrooms = document.getElementById('bedrooms').value.trim();
  const location = document.getElementById('location').value.trim();

  const response = await fetch(
    '/predict?area=' + area + '&bedrooms=' + bedrooms + '&location=' + location
  );

  const data = await response.json();
  result.textContent = data.predicted_price;
});
