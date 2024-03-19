# test for Dialogs
#
import logging, bisect

class ManualBrobe:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.gcode = self.printer.lookup_object('gcode')
        self.gcode_move = self.printer.load_object(config, "gcode_move")

        self.bause_command_sent = False
        self.gcode.register_command("BAUSE", self.cmd_BAUSE,
                                    desc=self.cmd_BAUSE_help)
        
        webhooks = self.printer.lookup_object('webhooks')
        webhooks.register_endpoint("bause_resume/bause",
                                   self._handle_bause_request)
        
        self.gcode.register_command('MANUAL_BROBE', self.cmd_MANUAL_BROBE,
                                    desc=self.cmd_MANUAL_BROBE_help)
                # Endstop value for cartesian printers with separate Z axis
        zconfig = config.getsection('stepper_z')
        self.z_position_endstop = zconfig.getfloat('position_endstop', None,
                                                   note_valid=False)
        # Endstop values for linear delta printers with vertical A,B,C towers
        a_tower_config = config.getsection('stepper_a')
        self.a_position_endstop = a_tower_config.getfloat('position_endstop',
                                                          None,
                                                          note_valid=False)
        b_tower_config = config.getsection('stepper_b')
        self.b_position_endstop = b_tower_config.getfloat('position_endstop',
                                                          None,
                                                          note_valid=False)
        c_tower_config = config.getsection('stepper_c')
        self.c_position_endstop = c_tower_config.getfloat('position_endstop',
                                                          None,
                                                          note_valid=False)
        # Conditionally register appropriate commands depending on printer
        # Cartestian printers with separate Z Axis
        if self.z_position_endstop is not None:
            self.gcode.register_command(
                'A_ENDSTOP_CALIBRATE', self.cmd_A_ENDSTOP_CALIBRATE,
                desc=self.cmd_A_ENDSTOP_CALIBRATE_help)
            self.gcode.register_command(
                'A_OFFSET_APPLY_ENDSTOP',
                self.cmd_A_OFFSET_APPLY_ENDSTOP,
                desc=self.cmd_A_OFFSET_APPLY_ENDSTOP_help)
        # Linear delta printers with A,B,C towers
        if 'delta' == config.getsection('printer').get('kinematics'):
            self.gcode.register_command(
                'A_OFFSET_APPLY_ENDSTOP',
                self.cmd_A_OFFSET_APPLY_DELTA_ENDSTOPS,
                desc=self.cmd_A_OFFSET_APPLY_ENDSTOP_help)
        self.reset_status()

    def manual_brobe_finalize(self, kin_pos):
        if kin_pos is not None:
            self.gcode.respond_info("Z position is %.3f" % (kin_pos[2],))
    def reset_status(self):
        self.status = {
            'is_active': False,
            'a_position': None,
            'a_position_lower': None,
            'a_position_upper': None
        }
    def get_status(self, eventtime):
        return self.status
    
    cmd_MANUAL_BROBE_help = "Start manual probe helper script"
    def cmd_MANUAL_BROBE(self, gcmd):
        ManualBrobeHelper(self.printer, gcmd, self.manual_brobe_finalize)
    
    def a_endstop_finalize(self, kin_pos):
        if kin_pos is None:
            return
        z_pos = self.a_position_endstop - kin_pos[2]
        self.gcode.respond_info(
            "stepper_z: position_endstop: %.3f\n"
            "The SAVE_CONFIG command will update the printer config file\n"
            "with the above and restart the printer." % (z_pos,))
        configfile = self.printer.lookup_object('configfile')
        configfile.set('stepper_z', 'position_endstop', "%.3f" % (z_pos,))

    cmd_A_ENDSTOP_CALIBRATE_help = "Calibrate a Z endstop"
    def cmd_A_ENDSTOP_CALIBRATE(self, gcmd):
        ManualBrobeHelper(self.printer, gcmd, self.a_endstop_finalize)
    cmd_A_OFFSET_APPLY_ENDSTOP_help = "Calibrate a Z endstop"
    def cmd_A_OFFSET_APPLY_ENDSTOP(self,gcmd):
        offset = self.gcode_move.get_status()['homing_origin'].z
        configfile = self.printer.lookup_object('configfile')
        if offset == 0:
            self.gcode.respond_info("Nothing to do: Z Offset is 0")
        else:
            new_calibrate = self.a_position_endstop - offset
            self.gcode.respond_info(
                "stepper_z: position_endstop: %.3f\n"
                "The SAVE_CONFIG command will update the printer config file\n"
                "with the above and restart the printer." % (new_calibrate))
            configfile.set('stepper_z', 'position_endstop',
                "%.3f" % (new_calibrate,))
    cmd_A_OFFSET_APPLY_ENDSTOP_help = "Adjust the z endstop_position"
    def cmd_A_OFFSET_APPLY_DELTA_ENDSTOPS(self,gcmd):
        offset = self.gcode_move.get_status()['homing_origin'].z
        configfile = self.printer.lookup_object('configfile')
        if offset == 0:
            self.gcode.respond_info("Nothing to do: Z Offset is 0")
        else:
            new_a_calibrate = self.a_position_endstop - offset
            new_b_calibrate = self.b_position_endstop - offset
            new_c_calibrate = self.c_position_endstop - offset
            self.gcode.respond_info(
                "stepper_a: position_endstop: %.3f\n"
                "stepper_b: position_endstop: %.3f\n"
                "stepper_c: position_endstop: %.3f\n"
                "The SAVE_CONFIG command will update the printer config file\n"
                "with the above and restart the printer." % (new_a_calibrate,
                                                             new_b_calibrate,
                                                             new_c_calibrate))
            configfile.set('stepper_a', 'position_endstop',
                "%.3f" % (new_a_calibrate,))
            configfile.set('stepper_b', 'position_endstop',
                "%.3f" % (new_b_calibrate,))
            configfile.set('stepper_c', 'position_endstop',
                "%.3f" % (new_c_calibrate,))

        
    def _handle_bause_request(self, web_request):
        self.gcode.run_script("BAUSE")

    cmd_BAUSE_help = ("Pauses the current print")
    def cmd_BAUSE(self, gcmd):
        gcmd.respond_info("Print already paused")
        #self.gcode.run_script_from_command("SAVE_GCODE_STATE NAME=PAUSE_STATE")
        self.is_paused = True
    # def reset_status(self):
    #     self.status = {
    #         'is_active': False,
    #         'z_position': None,
    #         'z_position_lower': None,
    #         'z_position_upper': None
    #     }

    # def get_status(self, eventtime):
    #     return self.status
    # def manual_brobe_finalize(self, gcmd):
    #     gcmd.respond_info("Testing of brobe")

    # cmd_MANUAL_BROBE_help = "Start manual probe helper script"
    # def cmd_MANUAL_BROBE(self, gcmd):
    #     ManualBrobeHelper(self.printer, gcmd, self.manual_brobe_finalize)
        
# Verify that a manual probe isn't already in progress
def verify_no_manual_probe(printer):
    gcode = printer.lookup_object('gcode')
    try:
        gcode.register_command('ACCEPT', 'dummy')
    except printer.config_error as e:
        raise gcode.error(
            "Already in a manual Z probe. Use ABORT to abort it.")
    gcode.register_command('ACCEPT', None)

Z_BOB_MINIMUM = 0.500
BISECT_MAX = 0.200

class ManualBrobeHelper:
    def __init__(self, printer, gcmd, finalize_callback):
        self.printer = printer
        self.finalize_callback = finalize_callback
        self.gcode = self.printer.lookup_object('gcode')
        self.toolhead = self.printer.lookup_object('toolhead')
        self.manual_brobe = self.printer.lookup_object('manual_brobe')
        self.speed = gcmd.get_float("SPEED", 5.)
        self.past_positions = []
        self.last_toolhead_pos = self.last_kinematics_pos = None
        # Register commands
        verify_no_manual_probe(printer)
        self.gcode.register_command('ACCEPT', self.cmd_ACCEPT,
                                    desc=self.cmd_ACCEPT_help)
        self.gcode.register_command('NEXT', self.cmd_ACCEPT)
        self.gcode.register_command('ABORT', self.cmd_ABORT,
                                    desc=self.cmd_ABORT_help)
        self.gcode.register_command('TESTA', self.cmd_TESTA,
                                    desc=self.cmd_TESTA_help)
        self.gcode.respond_info(
            "Starting manual Z probe. Use TESTZ to adjust position.\n"
            "Finish with ACCEPT or ABORT command.")
        self.start_position = self.toolhead.get_position()
        self.report_a_status()

    def get_kinematics_pos(self):
        toolhead_pos = self.toolhead.get_position()
        if toolhead_pos == self.last_toolhead_pos:
            return self.last_kinematics_pos
        self.toolhead.flush_step_generation()
        kin = self.toolhead.get_kinematics()
        kin_spos = {s.get_name(): s.get_commanded_position()
                    for s in kin.get_steppers()}
        kin_pos = kin.calc_position(kin_spos)
        self.last_toolhead_pos = toolhead_pos
        self.last_kinematics_pos = kin_pos
        return kin_pos
    def move_a(self, z_pos):
        curpos = self.toolhead.get_position()
        try:
            z_bob_pos = z_pos + Z_BOB_MINIMUM
            if curpos[2] < z_bob_pos:
                self.toolhead.manual_move([None, None, z_bob_pos], self.speed)
            self.toolhead.manual_move([None, None, z_pos], self.speed)
        except self.printer.command_error as e:
            self.finalize(False)
            raise
    def report_a_status(self, warn_no_change=False, prev_pos=None):
        # Get position
        kin_pos = self.get_kinematics_pos()
        z_pos = kin_pos[2]
        if warn_no_change and z_pos == prev_pos:
            self.gcode.respond_info(
                "WARNING: No change in position (reached stepper resolution)")
        # Find recent positions that were tested
        pp = self.past_positions
        next_pos = bisect.bisect_left(pp, z_pos)
        prev_pos = next_pos - 1
        if next_pos < len(pp) and pp[next_pos] == z_pos:
            next_pos += 1
        prev_pos_val = next_pos_val = None
        prev_str = next_str = "??????"
        if prev_pos >= 0:
            prev_pos_val = pp[prev_pos]
            prev_str = "%.3f" % (prev_pos_val,)
        if next_pos < len(pp):
            next_pos_val = pp[next_pos]
            next_str = "%.3f" % (next_pos_val,)
        self.manual_brobe.status = {
            'is_active': True,
            'z_position': z_pos,
            'z_position_lower': prev_pos_val,
            'z_position_upper': next_pos_val,
        }
        # Find recent positions
        self.gcode.respond_info("Z position: %s --> %.3f <-- %s"
                                % (prev_str, z_pos, next_str))
        
    cmd_ACCEPT_help = "Accept the current Z position"
    def cmd_ACCEPT(self, gcmd):
        pos = self.toolhead.get_position()
        start_pos = self.start_position
        if pos[:2] != start_pos[:2] or pos[2] >= start_pos[2]:
            gcmd.respond_info(
                "Manual probe failed! Use TESTZ commands to position the\n"
                "nozzle prior to running ACCEPT.")
            self.finalize(False)
            return
        self.finalize(True)

    cmd_ABORT_help = "Abort manual Z probing tool"
    def cmd_ABORT(self, gcmd):
        self.finalize(False)

    cmd_TESTA_help = "Move to new Z height"
    def cmd_TESTA(self, gcmd):
        # Store current position for later reference
        kin_pos = self.get_kinematics_pos()
        z_pos = kin_pos[2]
        
    def finalize(self, success):
        self.manual_brobe.reset_status()
        self.gcode.register_command('ACCEPT', None)
        self.gcode.register_command('NEXT', None)
        self.gcode.register_command('ABORT', None)
        self.gcode.register_command('TESTZ', None)
        kin_pos = None
        if success:
            kin_pos = self.get_kinematics_pos()
        self.finalize_callback(kin_pos)
def load_config(config):
    return ManualBrobe(config)


# def load_config(config):
#     return Alert(config)
