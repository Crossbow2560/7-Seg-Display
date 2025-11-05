`timescale 1ns/1ps

module seg7v_tb;
    reg clk;
    reg [3:0] nibble;
    wire [6:0] seg;
    wire [6:0] seg_ordered;
    assign seg_ordered = {seg[0], seg[1], seg[2], seg[3], seg[4], seg[5], seg[6]};

    // DUT
    seg7v uut (
        .clk(clk),
        .nibble(nibble),
        .seg(seg)
    );

    // 10 ns clock period
    initial clk = 0;
    always #5 clk = ~clk;

    initial begin
        $dumpfile("seg7v_tb.vcd");
        $dumpvars(0, seg7v_tb);
        $display("clk\tseg1..7");

        // loop through all the numbers from (0-15)
        nibble = 4'b0000; @(posedge clk); @(negedge clk); #1; $display("%b\t%b", clk, seg_ordered); // 0
        nibble = 4'b0001; @(posedge clk); @(negedge clk); #1; $display("%b\t%b", clk, seg_ordered); // 1
        nibble = 4'b0010; @(posedge clk); @(negedge clk); #1; $display("%b\t%b", clk, seg_ordered); // 2
        nibble = 4'b0011; @(posedge clk); @(negedge clk); #1; $display("%b\t%b", clk, seg_ordered); // 3
        nibble = 4'b0100; @(posedge clk); @(negedge clk); #1; $display("%b\t%b", clk, seg_ordered); // 4
        nibble = 4'b0101; @(posedge clk); @(negedge clk); #1; $display("%b\t%b", clk, seg_ordered); // 5
        nibble = 4'b0110; @(posedge clk); @(negedge clk); #1; $display("%b\t%b", clk, seg_ordered); // 6
        nibble = 4'b0111; @(posedge clk); @(negedge clk); #1; $display("%b\t%b", clk, seg_ordered); // 7
        nibble = 4'b1000; @(posedge clk); @(negedge clk); #1; $display("%b\t%b", clk, seg_ordered); // 8
        nibble = 4'b1001; @(posedge clk); @(negedge clk); #1; $display("%b\t%b", clk, seg_ordered); // 9
        nibble = 4'b1010; @(posedge clk); @(negedge clk); #1; $display("%b\t%b", clk, seg_ordered); // 10

        // custom test cases (2, 5, 8, 3)
        nibble = 4'b0010; @(posedge clk); @(negedge clk); #1; $display("%b\t%b", clk, seg_ordered); 
        nibble = 4'b0101; @(posedge clk); @(negedge clk); #1; $display("%b\t%b", clk, seg_ordered);
        nibble = 4'b1000; @(posedge clk); @(negedge clk); #1; $display("%b\t%b", clk, seg_ordered);
        nibble = 4'b0011; @(posedge clk); @(negedge clk); #1; $display("%b\t%b", clk, seg_ordered);

        @(posedge clk);
        #10 $finish;
    end
endmodule