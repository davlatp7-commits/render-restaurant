/*
 * Waiter dashboard polling script
 *
 * This script periodically queries the ``/waiter/check_new`` endpoint to
 * determine whether a new order has been created and whether any orders
 * remain in the default ``новый`` status.  When a brand‑new order is
 * detected the page will play a short notification sound and then
 * automatically refresh to show the new order in the list.  While there
 * are orders that have not yet been assigned a status other than
 * ``новый`` the sound will play on each poll to remind the waiter to
 * acknowledge the order.
 */

let lastOrderId = null;

// Preload the notification sound.  If the file cannot be loaded the
// Audio constructor will fail silently.
const audio = new Audio("/static/sound/dink.mp3");
// We don't want the sound to loop endlessly; instead we'll reset the
// playback position manually when needed.
audio.loop = false;

function checkForNewOrders() {
    fetch("/waiter/check_new")
        .then(response => response.json())
        .then(data => {
            // Initialise lastOrderId on first poll
            if (lastOrderId === null) {
                lastOrderId = data.latest_id;
            } else {
                // If a newer order appears, play a sound and refresh the page
                if (data.latest_id > lastOrderId) {
                    lastOrderId = data.latest_id;
                    // reset playback position and play sound
                    audio.currentTime = 0;
                    audio.play().catch(() => {});
                    // reload the page after the sound finishes to display the new order
                    audio.onended = () => {
                        window.location.reload();
                    };
                    return;
                }
            }

            // If there are unassigned ("новый") orders, play the sound to
            // alert the waiter.  Only play if the audio is not already
            // playing to avoid overlapping sounds.
            if (data.unassigned) {
                if (audio.paused) {
                    audio.currentTime = 0;
                    audio.play().catch(() => {});
                }
            }
        })
        .catch(err => console.error("Ошибка при проверке заказов:", err));
}

// Poll every 5 seconds.  A shorter interval could result in too many
// database queries; adjust as needed.
setInterval(checkForNewOrders, 5000);
