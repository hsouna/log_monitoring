var socket = io();
socket.on('connect', function () {
    socket.emit('my event', {
        data: 'I\'m connected!'
    });
});
/* socket.on('errors', function (json) {
    console.log(json)
});
socket.on('ip', function (json) {
    console.log(json)
});
socket.on('notFound', function (json) {
    console.log(json)
});
socket.on('ade', function (json) {
    console.log(json)
});
socket.on('perso', function (json) {
    console.log(json)
}); */