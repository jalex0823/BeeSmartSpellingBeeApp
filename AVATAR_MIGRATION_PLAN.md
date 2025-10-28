# Avatar Migration Plan: OBJ to GLB Conversion

## 15 Avatars to Replace (Non-Rendering White Blobs)

### Current Structure Analysis:
```
✗ doctor-bee/          - INCOMPLETE (only DoctorBee.obj, missing MTL + textures)
✗ beedoctor/           - DUPLICATE of doctor-bee? Has BeeDoctor.mtl, DoctorBee.obj
✗ beeknight/           - KnightBee.obj + KnightBee.mtl (rendering issue)
✗ builderbee/          - BuilderBee.obj + BuilderBee.mtl (rendering issue)
✗ buzzbotbee/          - BuzzbotBee.obj + BuzzbotBee.mtl (rendering issue)
✗ buzzhero/            - BuzzheroBee.obj + BuzzHero.mtl (rendering issue)
✗ detectivebee/        - DetectiveBee.obj + DetectiveBee.mtl (rendering issue)
✗ explorerbee/         - ExplorerBee.obj + ExplorerBee.mtl (rendering issue)
✗ frankenbee/          - FrankenBee.obj + Frankenbee.mtl (rendering issue)
✗ motorcyclebuzzbee/   - MotorcyclebuzzBee.obj + MotorcycleBuzzBee.mtl (rendering issue)
✗ queenbeemajesty/     - QueenmajestyBee.obj + QueenBeeMajesty.mtl (rendering issue)
✗ spacebeeexplorer/    - SpaceexplorerBee.obj + SpaceBeeExplorer.mtl (rendering issue)
✗ superbeehero/        - SuperheroBee.obj + SuperBeeHero.mtl (rendering issue)
✗ seabee/              - SeaBee.obj + SeaBee.mtl (rendering issue)

### Working Avatars (Keep As-Is):
✓ al-bee/              - AlBee.obj + AlBee.mtl + textures
✓ anxious-bee/         - AnxiousBee.obj + AnxiousBee.mtl + textures
✓ bee-diva/            - Bee_Diva texture + obj + mtl
✓ mascot-bee/          - MascotBee.obj + MascotBee.mtl + textures (working)
✓ monster-bee/         - MonsterBee.obj + MonsterBee.mtl + textures
✓ professor-bee/       - ProfessorBee.obj + ProfessorBee.mtl + textures
✓ rocker-bee/          - RockerBee.obj + RockerBee.mtl + textures
✓ vamp-bee/            - VampBee.obj + VampBee.mtl + textures
✓ ware-bee/            - WareBee.obj + WareBee.mtl + textures
✓ zom-bee/             - ZomBee.obj + ZomBee.mtl + textures
```

## Step-by-Step Migration Plan

### STEP 1: Clean Up Duplicates & Incomplete Files
1. Move `/doctor-bee/` to backup (it's incomplete, only has obj)
2. Keep `/beedoctor/` as the primary doctor bee folder
3. Document slug mapping for database

### STEP 2: Backup Current State
```bash
# Before making any changes:
1. Backup /static/assets/avatars/ folder
2. Export Avatar table from database
3. Create git branch: git checkout -b avatar-obj-to-glb-migration
```

### STEP 3: Delete Old OBJ/MTL Files
For each of the 14 folders (after consolidating doctor-bee):
```
Remove:
  - *.obj files
  - *.mtl files
  - Keep: *.png texture files (we'll reuse these)
```

### STEP 4: Add GLB Files
Replace with:
```
Add:
  - avatar-name.glb (single binary file containing model + textures)
  - Keep existing *.png for thumbnail/UI purposes
```

### STEP 5: Update Three.js Avatar Loader
Modify avatar loading code in:
- `templates/quiz.html`
- `templates/speed_round_quiz.html`
- `templates/battle.html` (if exists)

Add GLB loader support:
```javascript
// Check if GLB file exists, fall back to OBJ
if (hasGLB) {
    useGLBLoader(); // GLBDracoLoader
} else {
    useOBJLoader(); // OBJLoader + MTLLoader
}
```

### STEP 6: Database Model Updates
Check if `models.py` Avatar model needs updates for GLB support.
Likely no changes needed - just loading different file format.

### STEP 7: Testing Checklist
- [ ] Each GLB avatar loads in desktop browser
- [ ] Each GLB avatar loads on iOS mobile
- [ ] Each GLB avatar loads on Android mobile
- [ ] No performance degradation
- [ ] No texture loading errors
- [ ] Avatar selection works properly
- [ ] Battle system uses correct avatars

### STEP 8: Deployment
```bash
1. Commit: "Replace 14 non-rendering OBJ avatars with GLB models"
2. Push to main branch
3. Deploy to Railway
4. Monitor for errors in production
5. Rollback plan: git revert if issues
```

## File Structure After Migration

```
/static/assets/avatars/
├── beedoctor/
│   ├── DoctorBee.png         (texture)
│   ├── DoctorBee!.png        (error state)
│   └── DoctorBee.glb         (NEW - replaces .obj/.mtl)
├── beeknight/
│   ├── KnightBee.png
│   ├── KnightBee!.png
│   └── KnightBee.glb         (NEW)
├── builderbee/
│   ├── BuilderBee.png
│   ├── BuilderBee!.png
│   └── BuilderBee.glb        (NEW)
... (etc for all 14 avatars)
```

## Important Notes

1. **GLB Format**: Single binary file containing geometry + textures (more efficient than OBJ+MTL)
2. **Draco Compression**: GLB supports Draco compression for smaller file sizes
3. **Performance**: GLB typically loads faster than OBJ+MTL combination
4. **Compatibility**: Need to add GLB loader to Three.js scene
5. **Texture References**: GLB files should have embedded textures or relative paths

## Rollback Plan

If issues occur:
```bash
git checkout main -- .
rm -rf /static/assets/avatars/
git restore /static/assets/avatars/
# Revert database if needed from backup
```

## Success Criteria

✓ All 14 avatars render correctly (no white blobs)
✓ No texture loading errors
✓ Performance same or better than OBJ
✓ Mobile platforms work correctly
✓ Battle system integrates properly
✓ Zero impact to other app features
