const form = document.getElementById("giftForm");
const giftsContainer = document.getElementById("gifts");
const emptyState = document.getElementById("emptyState");

async function fetchGifts() {
	try {
		const res = await fetch("/gifts");
		if (!res.ok) throw new Error("Failed to load gifts");
		return await res.json();
	} catch (err) {
		console.error(err);
		return [];
	}
}

function renderGift({ name = "", gift = "" }) {
	const card = document.createElement("div");
	card.className = `
		rounded-xl
		border border-neutral-800
		bg-neutral-900/60
		p-4
		transition
		hover:bg-neutral-900
	`;

	const title = document.createElement("h3");
	title.className = "text-sm font-medium text-neutral-100";
	title.textContent = name;

	const description = document.createElement("p");
	description.className = "mt-1 text-sm text-neutral-400";
	description.textContent = gift;

	card.append(title, description);
	return card;
}

async function loadGifts() {
	giftsContainer.innerHTML = "";
	emptyState.classList.add("hidden");

	const gifts = await fetchGifts();

	if (gifts.length === 0) {
		emptyState.classList.remove("hidden");
		return;
	}

	for (const gift of gifts) {
		giftsContainer.appendChild(renderGift(gift));
	}
}

form.addEventListener("submit", async (event) => {
	event.preventDefault();

	const formData = new FormData(form);
	const name = formData.get("name")?.trim();
	const gift = formData.get("gift")?.trim();

	if (!name || !gift) return;

	try {
		const res = await fetch("/gifts", {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ name, gift }),
		});

		if (!res.ok) {
			const data = await res.json();
			alert(data.error);
			throw new Error(data.error);
		}

		form.reset();
		await loadGifts();
	} catch (err) {
		console.error("Failed to submit gift:", err);
	}
});

loadGifts();
