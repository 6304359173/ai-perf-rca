const express = require("express");

const app = express();

app.use(express.json());

// -----------------------------
// GET PRODUCTS
// -----------------------------
app.get("/products", (req, res) => {

    const products = [
        {
            id: 101,
            name: "Laptop",
            price: 75000
        },
        {
            id: 102,
            name: "Mobile",
            price: 30000
        },
        {
            id: 103,
            name: "Headphones",
            price: 5000
        }
    ];

    res.json(products);
});


// -----------------------------
// CREATE ORDER
// -----------------------------
let orders = [];
let orderId = 1000;

app.post("/orders", (req, res) => {

    const order = {

        orderId: ++orderId,

        customerId: req.body.customerId,

        productId: req.body.productId,

        quantity: req.body.quantity,

        status: "CREATED"
    };

    orders.push(order);

    res.status(201).json(order);
});


// -----------------------------
// GET ORDER
// -----------------------------
app.get("/orders/:orderId", (req, res) => {

    const id = Number(req.params.orderId);

    const order = orders.find(
        o => o.orderId === id
    );

    if (!order) {

        return res.status(404).json({
            message: "Order not found"
        });
    }

    res.json(order);
});


// -----------------------------
// HEALTH CHECK
// -----------------------------
app.get("/health", (req, res) => {

    res.json({
        status: "UP"
    });

});


// -----------------------------
// START SERVER
// -----------------------------
const PORT = 3002;

app.listen(PORT, () => {

    console.log(
        `Order service running on port ${PORT}`
    );

});