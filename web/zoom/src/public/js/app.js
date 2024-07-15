const messageList = document.querySelector("ul")
const messageForm = document.querySelector("form")

const socket = new WebSocket(`ws://${window.location.host}`);

socket.addEventListener("open", () => {
        console.log("connected to Server")
})

socket.addEventListener("message", (message) => {
    console.log("New Message:", message.data)
})

socket.addEventListener("close", () => {
    console.log("socket closed")
})

setTimeout(() => {
    socket.send("hello from the browser")
}, 10000)

function handleSubmit(event) {
    event.preventDefault()
    const input = messageForm.querySelector("input")
    socket.send(input.value)
    console.log(input.value)
    input.value = ""
}
messageForm.addEventListener("submit", handleSubmit)