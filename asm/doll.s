@ The Soul Doll adapter, answered in ROM: docs/re/doll.md, decision D8. A player has no adapter, and Small Cave can't be left without Reborn reading a doll.
@ One Hexadragon doll. What the game writes to it stays in flash sector 15, which the save doesn't use, so it survives power-off like a real doll's memory.
@ Status word 0x03006D48: 1 busy, 2 present, 0x10 writing, 0x20 reading, 0x8000 no reply. Bits 8-11 are this patch's countdown, in frames of the doll task.

@ Entry points at fixed offsets, for the hooks: tools/insert.py, DOLL_ENTRY.
	b doll_test
	b doll_read
	b doll_write
	b doll_tick

@ Replaces 0x0BADA8: is this status bit up? r0 = index into the mask table. Always present, never "no reply", whatever the link IRQ says.
doll_test:
	lsls r0, r0, #0x18
	lsrs r0, r0, #0x17
	ldr r2, L_status
	ldrh r1, [r2]
	ldr r3, L_no_reply
	ands r1, r3
	movs r3, #2
	orrs r1, r3
	strh r1, [r2]
	ldr r2, L_masks
	ldrh r0, [r2, r0]
	ands r0, r1
	beq dt_done
	movs r0, #1
dt_done:
	bx lr

@ Replaces 0x0E4948: r0 buffer, r1 size, r2 doll offset. The 0x80-byte image comes from flash, the 0x380-byte header is blank but for the doll's type.
doll_read:
	push {r4, r5, lr}
	mov r4, r0
	mov r5, r1
	cmp r1, #0x80
	bne dr_header
	movs r0, #15
	movs r1, #0
	mov r2, r4
	mov r3, r5
	ldr r5, L_flash_read
	bl via_r5
	ldr r0, [r4]
	adds r0, #1
	bne dr_busy
	movs r0, #0x20		@ never written: a blank image is the key alone, which decrypts to zeros, and the game takes it as a new doll
	ldr r1, L_key
	mov r2, r4
dr_fill:
	stm r2!, {r1}
	subs r0, #1
	bne dr_fill
	b dr_busy
dr_header:
	movs r1, #0
	mov r2, r4
	lsrs r0, r5, #2
dr_zero:
	stm r2!, {r1}
	subs r0, #1
	bne dr_zero
	ldr r1, L_type_at
	movs r0, #0x2C		@ table 0x466E74: species 0, Hexadragon, the story's partner
	strb r0, [r4, r1]
dr_busy:
	movs r0, #0x23		@ busy, reading, present: the Reborn task has to see busy before it clears (0x0C8490)
	bl set_busy
	pop {r4, r5}
	pop {r0}
	bx r0

@ Replaces 0x0E488C: r0 buffer, r1 size, r2 doll offset. Only the image is kept; the game reads the header's type byte alone.
doll_write:
	push {r4, r5, lr}
	cmp r1, #0x80
	bne dw_busy
	movs r2, #15
	ldr r5, L_flash_write		@ 0x0C2770: erase, program, verify; r0 buffer, r1 bytes to verify, r2 sector
	bl via_r5
dw_busy:
	movs r0, #0x13
	bl set_busy
	pop {r4, r5}
	pop {r0}
	bx r0

set_busy:
	movs r1, #0x80
	lsls r1, r1, #4		@ 8 frames
	orrs r0, r1
	ldr r1, L_status
	strh r0, [r1]
	bx lr

via_r5:
	bx r5

@ Hooks 0x0BADD4, the doll task, once a frame: counts the transfer down, then runs what the far jump took and goes back.
doll_tick:
	push {r4, lr}
	mov r4, r0
	ldr r1, L_status
	ldrh r2, [r1]
	movs r3, #0xF0
	lsls r3, r3, #4
	tst r2, r3
	beq dk_done
	subs r2, #0x80
	subs r2, #0x80
	tst r2, r3
	bne dk_store
	movs r3, #0x31
	bics r2, r3
dk_store:
	strh r2, [r1]
dk_done:
	ldrh r0, [r4, #6]
	ldr r3, L_tick_ret
	cmp r0, #0x33
	bx r3

	.align 2
L_status:	.word 0x03006D48
L_no_reply:	.word 0x00007FFF
L_masks:	.word 0x08434E78
L_flash_read:	.word 0x080E5435
L_flash_write:	.word 0x080C2771
L_key:	.word 0xA8262CDB
L_type_at:	.word 0x00000302
L_tick_ret:	.word 0x080BADDD
