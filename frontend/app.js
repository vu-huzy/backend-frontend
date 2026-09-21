const form = document.getElementById("item-form");
const API_URL = "http://127.0.0.1:8000";

form.addEventListener("submit", async function (e) {
	e.preventDefault();
	await fetch(`${API_URL}/items`, {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify({
			name: form.elements.name.value,
			price: Number(form.elements.price.value),
		}),
	});
	form.reset();
	fetchData();
});

async function fetchData() {
	let tbody = document.querySelector("tbody");
	tbody.innerHTML = null;

	try {
		const response = await fetch(`${API_URL}/items?skip=0&limit=10`);
		const data = await response.json();
		if (data) {
			for (const item of data.items) {
				let row = document.createElement("tr");
				row.innerHTML = `
					<td>${item.id}</td>
					<td>${item.name}</td>
					<td>${item.price}</td>
					<td>
						<button onclick="handleDelete(${item.id})">Delete</button>
					</td>
				`;
				tbody.appendChild(row);
			}
		}
	} catch (error) {
		console.error(error);
	}
}

async function handleDelete(itemId) {
	try {
		await fetch(`${API_URL}/items/${itemId}`, {
			headers: { "Content-Type": "application/json" },
			method: "DELETE",
		});
		await fetchData();
	} catch (error) {
		console.error(error);
	}
}

document.getElementById("cancel-button").onclick = () => form.reset();
fetchData();
