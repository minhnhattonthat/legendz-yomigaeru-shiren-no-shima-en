@ Variable-width text for the two bitmap renderers (docs/re/vwf.md). Assembled by tools/asm_thumb.py; @NAME@ values come from tools/insert.py.
@ A text column is 2 stacked tiles: 0x40 bytes, 16 rows of one word each, so pixel column x of a row lives in tile column x / 8.

@ Entry points at fixed offsets, for the hooks: tools/insert.py, ENTRY.
	b vwf_open
	b vwf_static
	b vwf_type
	b vwf_br
	b vwf_tag
	nop

@ Replaces 0x0A311C, the speaker tag: r0=tag (+2 x, +4 y, +8 text, +E tile base, +12 its 8 OBJ slots). Draws the name into a 64x16 buffer on the stack,
@ laid out as vwf_rows lays out VRAM, then sends each column as a tall OBJ with the game's own loader, which copies at once. Font 2's colours are the tag font's.
vwf_tag:
	push {r4, r5, r6, r7, lr}
	mov r6, r0
	sub sp, #508
	sub sp, #116
	add r0, sp, #0x30
	movs r1, #0
	movs r2, #0x90
vtg_clear:
	stm r0!, {r1}
	subs r2, #1
	bne vtg_clear
	movs r0, #1
	str r0, [sp, #0x2c]
	add r7, sp, #0xc
	add r4, sp, #0x3c
	movs r5, #0
	ldr r3, [r6, #8]
vtg_text:
	ldrh r0, [r3]
	ldr r1, L_ffc0
	cmp r0, r1
	bhs vtg_send
	add r1, sp, #0x230
	cmp r4, r1
	bhs vtg_send
	adds r3, #2
	lsrs r1, r0, #10
	beq vtg_one
	bl vwf_split
	push {r1}
	bl vr_draw
	pop {r0}
vtg_one:
	bl vr_draw
	b vtg_text
vtg_send:
	add r0, sp, #0x3c
	subs r4, r4, r0
	lsrs r4, r4, #6
	adds r4, #1
	cmp r4, #8
	ble vtg_count
	movs r4, #8
vtg_count:
	movs r5, #0
vtg_obj:
	cmp r5, r4
	bge vtg_done
	lsls r0, r5, #1
	ldrh r1, [r6, #0xe]
	adds r0, r0, r1
	adds r0, #0x5a
	mov r1, sp
	strh r0, [r1]
	movs r0, #0xf
	strh r0, [r1, #2]
	movs r2, #2
	ldrsh r0, [r6, r2]
	adds r0, r0, r5
	adds r0, #9
	lsls r0, r0, #3
	strh r0, [r1, #4]
	movs r2, #4
	ldrsh r0, [r6, r2]
	lsls r0, r0, #3
	adds r0, #2
	strh r0, [r1, #8]
	movs r0, #0xff
	strh r0, [r1, #0xc]
	ldr r0, L_tagframes
	lsls r2, r5, #4
	adds r0, r0, r2
	str r0, [sp, #0x10]
	add r0, sp, #0x30
	subs r0, #2
	str r0, [sp, #0x14]
	movs r0, #0
	str r0, [sp, #0x18]
	mov r0, sp
	ldr r1, L_objnew
	bl vtg_call
	mov r0, sp
	ldrh r1, [r0, #0x1c]
	mov r0, r6
	adds r0, #0x12
	strb r1, [r0, r5]
	adds r5, #1
	b vtg_obj
vtg_done:
	add sp, #508
	add sp, #116
	pop {r4, r5, r6, r7}
	pop {r0}
	bx r0
vtg_call:
	bx r1

@ Hook at 0x0A5786, in the typewriter's window open: r5=descriptor r6=map base r7=tile entry r8=blank sb=stride sl=VRAM, [sp+4]=fill
vwf_open:
	sub sp, #52
	mov r0, r7
	str r0, [sp, #0]
	mov r0, r8
	str r0, [sp, #4]
	ldr r0, [sp, #56]
	str r0, [sp, #8]
	mov r0, sl
	str r0, [sp, #28]
	mov r2, sb
	ldrb r0, [r5, #5]
	muls r0, r2, r0
	ldrb r1, [r5, #4]
	adds r0, r0, r1
	lsls r0, r0, #1
	adds r0, r6, r0
	str r0, [sp, #24]
	movs r0, #0
	str r0, [sp, #40]
	str r0, [sp, #44]
	bl vwf_ctx
	add sp, #52
	ldr r0, L_open_ret
	bx r0

@ Hook at 0x0A594C, in the instant renderer: r3=VRAM ip=map r5=descriptor r6=fill r7=stride r8=blank
vwf_static:
	sub sp, #52
	ldrh r0, [r5, #0xa]
	str r0, [sp, #0]
	mov r0, r8
	str r0, [sp, #4]
	str r6, [sp, #8]
	str r3, [sp, #28]
	mov r0, ip
	str r0, [sp, #24]
	ldrb r0, [r5, #2]
	lsls r0, r0, #2
	str r0, [sp, #40]
	movs r0, #1
	str r0, [sp, #44]
	mov r2, r7
	bl vwf_ctx
	add sp, #52
	ldr r0, L_static_ret
	bx r0

@ Fills the fields both entries read the same way, runs the rows. r2=stride, r5=descriptor, ctx at sp + 4 after the push.
vwf_ctx:
	push {lr}
	add r0, sp, #4
	lsls r2, r2, #1
	str r2, [r0, #16]
	ldrb r1, [r5, #7]
	str r1, [r0, #12]
	ldr r1, [r5, #0x10]
	str r1, [r0, #20]
	ldrb r1, [r5, #3]
	movs r2, #1
	ands r1, r2
	str r1, [r0, #32]
	ldrb r1, [r5, #8]
	str r1, [r0, #36]
	bl vwf_rows
	pop {r0}
	bx r0

@ r0=ctx: 0 tile entry, 4 blank, 8 fill, 12 w, 16 stride bytes, 20 text, 24 map, 28 VRAM, 32 font bit, 36 rows left, 40 top pad bytes, 44 draw, 48 row VRAM
vwf_rows:
	push {r4, r5, r6, r7, lr}
	mov r7, r0
vr_row:
	ldr r0, [r7, #36]
	cmp r0, #0
	beq vr_done
	subs r0, #1
	str r0, [r7, #36]
	ldr r0, [r7, #20]
	ldr r1, [r7, #32]
	ldr r2, [r7, #12]
	lsls r2, r2, #3
	bl vwf_measure
	mov r6, r1
	ldr r1, [r7, #32]
	adds r0, r0, r1
	adds r0, #7
	lsrs r5, r0, #3
	ldr r4, [r7, #28]
	str r4, [r7, #48]
	ldr r3, [r7, #24]
	movs r2, #0
vr_col:
	ldr r1, [r7, #12]
	cmp r2, r1
	bhs vr_cols_done
	ldr r0, [r7, #16]
	adds r0, r0, r3
	cmp r2, r5
	bhs vr_blank
	ldr r1, [r7, #0]
	strh r1, [r3]
	adds r1, #1
	strh r1, [r0]
	adds r1, #1
	str r1, [r7, #0]
	ldr r1, [r7, #8]
	movs r0, #16
vr_clear:
	stm r4!, {r1}
	subs r0, #1
	bne vr_clear
	b vr_next
vr_blank:
	ldr r1, [r7, #4]
	strh r1, [r3]
	strh r1, [r0]
vr_next:
	adds r3, #2
	adds r2, #1
	b vr_col
vr_cols_done:
	str r4, [r7, #28]
	ldr r0, [r7, #24]
	ldr r1, [r7, #16]
	lsls r1, r1, #1
	adds r0, r0, r1
	str r0, [r7, #24]
	ldr r0, [r7, #44]
	cmp r0, #0
	beq vr_line_end
	ldr r4, [r7, #48]
	ldr r0, [r7, #40]
	adds r4, r4, r0
	movs r5, #0
	ldr r3, [r7, #20]
vr_glyph:
	cmp r3, r6
	beq vr_line_end
	ldrh r0, [r3]
	adds r3, #2
	lsrs r1, r0, #10
	beq vr_single
	bl vwf_split
	push {r1}
	bl vr_draw
	pop {r0}
vr_single:
	bl vr_draw
	b vr_glyph
vr_line_end:
	mov r0, r6
	ldrh r1, [r0]
	ldr r2, L_fffd
	cmp r1, r2
	bne vr_keep
	adds r0, #2
vr_keep:
	str r0, [r7, #20]
	b vr_row
vr_done:
	pop {r4, r5, r6, r7}
	pop {r0}
	bx r0

@ One glyph of a row: r0=code r4=column VRAM r5=pen r7=ctx, keeps r3.
vr_draw:
	push {r3, lr}
	mov r1, r4
	mov r2, r5
	ldr r3, [r7, #32]
	bl vwf_glyph
	adds r5, r5, r0
	lsrs r0, r5, #3
	lsls r0, r0, #6
	adds r4, r4, r0
	movs r0, #7
	ands r5, r0
	pop {r3}
	pop {r0}
	bx r0

@ r0=a word of two letters (0x400 up) -> r0=first code, r1=second. Clobbers r2. L_pairs is the table's address less 0x400 * 4.
vwf_split:
	ldr r2, L_pairs
	lsls r0, r0, #2
	adds r2, r2, r0
	ldrh r0, [r2]
	ldrh r1, [r2, #2]
	bx lr

@ r0=text r1=font bit r2=max px -> r0=px, r1=where the line stops: a control word, or the first word past max (the game's own auto-wrap)
vwf_measure:
	push {r4, r5, lr}
	ldr r4, L_widths
	lsls r3, r1, #9
	adds r4, r4, r3
	movs r3, #0
	mov r1, r0
vm_loop:
	ldrh r5, [r1]
	ldr r0, L_ffc0
	cmp r5, r0
	bhs vm_done
	lsrs r0, r5, #10
	beq vm_single
	push {r1, r2}
	mov r0, r5
	bl vwf_split
	ldrb r0, [r4, r0]
	ldrb r1, [r4, r1]
	adds r5, r0, r1
	pop {r1, r2}
	b vm_add
vm_single:
	ldrb r5, [r4, r5]
vm_add:
	adds r0, r3, r5
	cmp r0, r2
	bgt vm_done
	mov r3, r0
	adds r1, #2
	b vm_loop
vm_done:
	mov r0, r3
	pop {r4, r5}
	pop {r2}
	bx r2

@ r0=code r1=column VRAM (row 0 of the glyph) r2=pen 0-7 r3=font bit -> r0=width
vwf_glyph:
	push {r4, r5, r6, r7, lr}
	ldr r4, L_widths
	lsls r5, r3, #9
	adds r4, r4, r5
	ldrb r4, [r4, r0]
	push {r4}
	ldr r5, L_fonts
	mov r6, r3
	lsls r3, r3, #2
	ldr r5, [r5, r3]
	lsls r3, r0, #1
	adds r3, r3, r0
	lsls r3, r3, #4
	adds r3, r3, r5
	adds r7, r2, r4
	lsls r2, r2, #2
	cmp r6, #0
	bne vg_outlined
	cmp r7, #8
	ble vg_nospill
	movs r7, #32
	subs r7, r7, r2
	b vg_mask
vg_nospill:
	movs r7, #0
vg_mask:
	lsls r5, r4, #2
	movs r4, #1
	lsls r4, r5
	subs r4, #1
	mov r5, r1
	adds r5, #48
	mov ip, r5
vg_row:
	ldm r3!, {r0}
	ands r0, r4
	mov r6, r4
	lsls r6, r2
	ldr r5, [r1]
	bics r5, r6
	mov r6, r0
	lsls r6, r2
	orrs r5, r6
	str r5, [r1]
	cmp r7, #0
	beq vg_row_end
	mov r6, r4
	lsrs r6, r7
	ldr r5, [r1, #0x40]
	bics r5, r6
	mov r6, r0
	lsrs r6, r7
	orrs r5, r6
	str r5, [r1, #0x40]
vg_row_end:
	adds r1, #4
	cmp r1, ip
	bne vg_row
vg_done:
	pop {r0}
	pop {r4, r5, r6, r7}
	pop {r1}
	bx r1

@ Font 2 has a transparent background and an outline a pixel wider than the advance: only its nonzero pixels are written, so outlines overlap cleanly.
vg_outlined:
	movs r7, #0
	cmp r2, #0
	beq vo_start
	movs r7, #32
	subs r7, r7, r2
vo_start:
	mov r5, r1
	adds r5, #48
	mov ip, r5
vo_row:
	ldm r3!, {r0}
	lsrs r5, r0, #1
	orrs r5, r0
	lsrs r6, r0, #2
	orrs r5, r6
	lsrs r6, r0, #3
	orrs r5, r6
	ldr r6, L_ones
	ands r5, r6
	lsls r6, r5, #4
	subs r5, r6, r5
	mov r6, r5
	lsls r6, r2
	ldr r4, [r1]
	bics r4, r6
	mov r6, r0
	lsls r6, r2
	orrs r4, r6
	str r4, [r1]
	cmp r7, #0
	beq vo_row_end
	mov r6, r5
	lsrs r6, r7
	ldr r4, [r1, #0x40]
	bics r4, r6
	mov r6, r0
	lsrs r6, r7
	orrs r4, r6
	str r4, [r1, #0x40]
vo_row_end:
	adds r1, #4
	cmp r1, ip
	bne vo_row
	b vg_done

@ Hook at 0x0A5590, the typewriter's glyph: r3=code r4=window. Pen in [window+0xE]; 0x03004C40 stays the cell the page arrow goes to.
vwf_type:
	push {r5, r6, r7}
	mov r0, r3
	lsrs r1, r0, #10
	beq vt_single
	bl vwf_split
	push {r1}
	bl vt_one
	pop {r0}
vt_single:
	bl vt_one
	pop {r5, r6, r7}
	ldr r0, L_type_ret
	bx r0

@ r0=code r4=window, clobbers r5-r7
vt_one:
	push {lr}
	ldr r1, [r4, #4]
	ldrh r2, [r4, #0xe]
	mov r6, r2
	ldrb r3, [r4, #0xc]
	movs r5, #1
	ands r3, r5
	bl vwf_glyph
	ldr r3, L_x
	ldrb r5, [r3]
	cmp r6, #0
	bne vt_same
	adds r5, #1
vt_same:
	adds r7, r6, r0
	subs r7, #1
	lsrs r7, r7, #3
	adds r5, r5, r7
	strb r5, [r3]
	adds r6, r6, r0
	lsrs r7, r6, #3
	lsls r7, r7, #6
	ldr r5, [r4, #4]
	adds r5, r5, r7
	str r5, [r4, #4]
	movs r7, #7
	ands r6, r7
	strh r6, [r4, #0xe]
	pop {r0}
	bx r0

@ Hook at 0x0A5572, the typewriter's newline: r4=window. Moves to the next line's first column, which the open laid out right after this line's last.
vwf_br:
	ldrh r0, [r4, #0xe]
	cmp r0, #0
	beq vb_aligned
	movs r0, #0
	strh r0, [r4, #0xe]
	ldr r1, [r4, #4]
	adds r1, #0x40
	str r1, [r4, #4]
vb_aligned:
	ldr r1, L_x
	ldr r0, L_x0
	ldrb r0, [r0]
	strb r0, [r1]
	ldr r1, L_y
	ldrb r0, [r1]
	adds r0, #2
	strb r0, [r1]
	ldr r0, L_type_ret
	bx r0

	.align 2
L_open_ret:	.word 0x080A5875
L_static_ret:	.word 0x080A5A65
L_type_ret:	.word 0x080A55FB
L_x:	.word 0x03004C40
L_y:	.word 0x03004C48
L_x0:	.word 0x03004C90
L_fffd:	.word 0x0000FFFD
L_ffc0:	.word 0x0000FFC0
L_ones:	.word 0x11111111
L_widths:	.word @WIDTHS@
L_pairs:	.word @PAIRS@
L_tagframes:	.word @TAGFRAMES@
L_objnew:	.word 0x08093FC5
L_fonts:	.word 0x087F6654
