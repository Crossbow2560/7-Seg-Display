`timescale 1ns/1ps

`include "../modules/dec.v"
`include "../modules/or4.v"
`include "../modules/or6.v"
`include "../modules/or7.v"
`include "../modules/or8.v"
`include "../modules/or9.v"


module seg7v(
    input wire clk,
    input wire [3:0] nibble,
    output wire [6:0] seg
);

wire [15:0] decoded_vals;

// instantiate 4-to-16 decoder (module name is Decoder4to16, ports A -> input, Y -> one-hot output)
Decoder4to16 decoder_inst(.A(nibble), .Y(decoded_vals));

// instantiate OR gates (module names are OR4/OR6/OR7/OR8/OR9)
OR8 led1(.a(decoded_vals[0]), .b(decoded_vals[2]), .c(decoded_vals[3]), .d(decoded_vals[5]), .e(decoded_vals[6]), .f(decoded_vals[7]), .g(decoded_vals[8]), .h(decoded_vals[9]), .y(seg[0]));
OR8 led2(.a(decoded_vals[0]), .b(decoded_vals[1]), .c(decoded_vals[2]), .d(decoded_vals[3]), .e(decoded_vals[4]), .f(decoded_vals[7]), .g(decoded_vals[8]), .h(decoded_vals[9]), .y(seg[1]));
OR9 led3(.a(decoded_vals[0]), .b(decoded_vals[1]), .c(decoded_vals[3]), .d(decoded_vals[4]), .e(decoded_vals[5]), .f(decoded_vals[6]), .g(decoded_vals[7]), .h(decoded_vals[8]), .i(decoded_vals[9]), .y(seg[2]));
OR7 led4(.a(decoded_vals[0]), .b(decoded_vals[2]), .c(decoded_vals[3]), .d(decoded_vals[5]), .e(decoded_vals[6]), .f(decoded_vals[8]), .g(decoded_vals[9]), .y(seg[3]));
OR4 led5(.a(decoded_vals[0]), .b(decoded_vals[2]), .c(decoded_vals[6]), .d(decoded_vals[8]), .y(seg[4]));
OR6 led6(.a(decoded_vals[0]), .b(decoded_vals[4]), .c(decoded_vals[5]), .d(decoded_vals[6]), .e(decoded_vals[8]), .f(decoded_vals[9]), .y(seg[5]));
OR7 led7(.a(decoded_vals[2]), .b(decoded_vals[3]), .c(decoded_vals[4]), .d(decoded_vals[5]), .e(decoded_vals[6]), .f(decoded_vals[8]), .g(decoded_vals[9]), .y(seg[6]));

endmodule