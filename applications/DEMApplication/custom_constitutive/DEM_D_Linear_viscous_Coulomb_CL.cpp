// Authors: M.A. Celigueta and S. Latorre (CIMNE)
// Date: October 2015

#include "DEM_D_Linear_viscous_Coulomb_CL.h"
#include "custom_elements/spheric_particle.h"

namespace Kratos {

    DEMDiscontinuumConstitutiveLaw::Pointer DEM_D_Linear_viscous_Coulomb::Clone() const {
        DEMDiscontinuumConstitutiveLaw::Pointer p_clone(new DEM_D_Linear_viscous_Coulomb(*this));
        return p_clone;
    }

    void DEM_D_Linear_viscous_Coulomb::SetConstitutiveLawInProperties(Properties::Pointer pProp, bool verbose) {
        if(verbose) KRATOS_INFO("DEM") << "Assigning DEM_D_Linear_viscous_Coulomb to Properties " << pProp->Id() << std::endl;
        pProp->SetValue(DEM_DISCONTINUUM_CONSTITUTIVE_LAW_POINTER, this->Clone());
        this->Check(pProp);
    }

    void DEM_D_Linear_viscous_Coulomb::Check(Properties::Pointer pProp) const {
        DEMDiscontinuumConstitutiveLaw::Check(pProp);
    }

    std::string DEM_D_Linear_viscous_Coulomb::GetTypeOfLaw() {
        std::string type_of_law = "Linear";
        return type_of_law;
    }

    /////////////////////////
    // DEM-DEM INTERACTION //
    /////////////////////////

    void DEM_D_Linear_viscous_Coulomb::InitializeContact(SphericParticle* const element1, SphericParticle* const element2, const double indentation) {
        
        //Get equivalent Radius
        const double my_radius       = element1->GetRadius();
        const double other_radius    = element2->GetRadius();
        const double radius_sum      = my_radius + other_radius;
        const double radius_sum_inv  = 1.0 / radius_sum;
        const double equiv_radius    = my_radius * other_radius * radius_sum_inv;

        //Get equivalent Young's Modulus
        const double my_young        = element1->GetYoung();
        const double other_young     = element2->GetYoung();
        const double my_poisson      = element1->GetPoisson();
        const double other_poisson   = element2->GetPoisson();
        const double equiv_young     = my_young * other_young / (other_young * (1.0 - my_poisson * my_poisson) + my_young * (1.0 - other_poisson * other_poisson));

        //Get equivalent Shear Modulus
        const double my_shear_modulus = 0.5 * my_young / (1.0 + my_poisson);
        const double other_shear_modulus = 0.5 * other_young / (1.0 + other_poisson);
        const double equiv_shear = 1.0 / ((2.0 - my_poisson)/my_shear_modulus + (2.0 - other_poisson)/other_shear_modulus);

        const double beta = 1.432;
        const double modified_radius =  equiv_radius * 0.31225; // r * sqrt(alpha * (2.0 - alpha)) = 0.31225
        mKn = beta * equiv_young * Globals::Pi * modified_radius;        // 2.0 * equiv_young * sqrt_equiv_radius;
        mKt = 4.0 * equiv_shear * mKn / equiv_young;
    }

    void DEM_D_Linear_viscous_Coulomb::CalculateForces(const ProcessInfo& r_process_info,
                                                       const double OldLocalElasticContactForce[3],
                                                       double LocalElasticContactForce[3],
                                                       double LocalDeltDisp[3],
                                                       double LocalRelVel[3],
                                                       double indentation,
                                                       double previous_indentation,
                                                       double ViscoDampingLocalContactForce[3],
                                                       double& cohesive_force,
                                                       SphericParticle* element1,
                                                       SphericParticle* element2,
                                                       bool& sliding, double LocalCoordSystem[3][3]) {

        InitializeContact(element1, element2, indentation);

        LocalElasticContactForce[2]  = CalculateNormalForce(element1, element2, indentation, LocalCoordSystem );
        cohesive_force               = CalculateCohesiveNormalForce(element1, element2, indentation);

        CalculateViscoDampingForce(LocalRelVel, ViscoDampingLocalContactForce, element1, element2);

        double normal_contact_force = LocalElasticContactForce[2] + ViscoDampingLocalContactForce[2];

        if (normal_contact_force < 0.0) {
            normal_contact_force = 0.0;
            ViscoDampingLocalContactForce[2] = -1.0 * LocalElasticContactForce[2];
        }

        double ElasticShearForceModulus;
        double MaximumAdmisibleShearForce;

        CalculateTangentialForceWithNeighbour(normal_contact_force, OldLocalElasticContactForce, LocalElasticContactForce, ViscoDampingLocalContactForce, LocalDeltDisp,
                                              LocalRelVel, sliding, element1, element2, indentation, previous_indentation, ElasticShearForceModulus, MaximumAdmisibleShearForce);

        double& elastic_energy = element1->GetElasticEnergy();
        CalculateElasticEnergyDEM(elastic_energy, indentation, LocalElasticContactForce);

        if (ElasticShearForceModulus > MaximumAdmisibleShearForce && MaximumAdmisibleShearForce != 0.0){
            double& inelastic_frictional_energy = element1->GetInelasticFrictionalEnergy();
            CalculateInelasticFrictionalEnergyDEM(inelastic_frictional_energy, ElasticShearForceModulus, LocalElasticContactForce);
        }

        double& inelastic_viscodamping_energy = element1->GetInelasticViscodampingEnergy();
        CalculateInelasticViscodampingEnergyDEM(inelastic_viscodamping_energy, ViscoDampingLocalContactForce, LocalDeltDisp);

    }

    Properties& DEM_D_Linear_viscous_Coulomb::GetPropertiesOfThisContact(SphericParticle* const element, SphericParticle* const neighbour){
        return element->GetProperties().GetSubProperties(neighbour->GetProperties().Id());
    }

    Properties& DEM_D_Linear_viscous_Coulomb::GetPropertiesOfThisContact(SphericParticle* const element, Condition* const neighbour){
        return element->GetProperties().GetSubProperties(neighbour->GetProperties().Id());
    }

    void DEM_D_Linear_viscous_Coulomb::CalculateViscoDampingForce(double LocalRelVel[3],
                                                                  double ViscoDampingLocalContactForce[3],
                                                                  SphericParticle* const element1,
                                                                  SphericParticle* const element2) {

        const double my_mass    = element1->GetMass();
        const double other_mass = element2->GetMass();

        const double equiv_mass = 1.0 / (1.0/my_mass + 1.0/other_mass);

        Properties& properties_of_this_contact = element1->GetProperties().GetSubProperties(element2->GetProperties().Id());
        const double damping_gamma = properties_of_this_contact[DAMPING_GAMMA];

        const double equiv_visco_damp_coeff_normal     = 2.0 * damping_gamma * sqrt(equiv_mass * mKn);
        const double equiv_visco_damp_coeff_tangential = 2.0 * damping_gamma * sqrt(equiv_mass * mKt);

        ViscoDampingLocalContactForce[0] = - equiv_visco_damp_coeff_tangential * LocalRelVel[0];
        ViscoDampingLocalContactForce[1] = - equiv_visco_damp_coeff_tangential * LocalRelVel[1];
        ViscoDampingLocalContactForce[2] = - equiv_visco_damp_coeff_normal     * LocalRelVel[2];
    }

    /////////////////////////
    // DEM-FEM INTERACTION //
    /////////////////////////

    void DEM_D_Linear_viscous_Coulomb::InitializeContactWithFEM(SphericParticle* const element, Condition* const wall, const double indentation, const double ini_delta) {
        //Get effective Radius
        const double my_radius           = element->GetRadius(); //Get equivalent Radius
        const double effective_radius    = my_radius - ini_delta;

        //Get equivalent Young's Modulus
        const double my_young            = element->GetYoung();
        //const double walls_young         = wall->GetYoung();
        const double walls_young         = wall->GetProperties()[YOUNG_MODULUS];
        const double my_poisson          = element->GetPoisson();
        //const double walls_poisson       = wall->GetPoisson();
        const double walls_poisson       = wall->GetProperties()[POISSON_RATIO];
        const double equiv_young         = my_young * walls_young / (walls_young * (1.0 - my_poisson * my_poisson) + my_young * (1.0 - walls_poisson * walls_poisson));

        //Get equivalent Shear Modulus
        const double my_shear_modulus    = 0.5 * my_young / (1.0 + my_poisson);
        const double walls_shear_modulus = 0.5 * walls_young / (1.0 + walls_poisson);
        const double equiv_shear         = 1.0 / ((2.0 - my_poisson)/my_shear_modulus + (2.0 - walls_poisson)/walls_shear_modulus);
        /*
        const double effective_young = my_young / (1.0 - my_poisson * my_poisson); //Equivalent Young Modulus for RIGID WALLS!
        const double effective_young = 0.5 * my_young / (1.0 - my_poisson * my_poisson); // Equivalent Young Modulus if the wall has the same E of the sphere
        //Infinite Young was imposed to the wall in the formula that includes both.
        //For flexible walls, the computation is different, Thornton 2012 proposes same Young for both)

        const double effective_shear = 0.5 * my_young / ((1.0 + my_poisson) * (2.0 - my_poisson)); //Equivalent Shear Modulus for RIGID WALLS!
        const double effective_shear = 0.25 * my_young / ((1.0 + my_poisson) * (2.0 - my_poisson)); //Equivalent Shear Modulus if the wall has the same E of the sphere
        //Infinite Shear was imposed to the wall in the formula that includes both.
        //For flexible walls, the computation is different, Thornton 2012 proposes same Shear for both)

        */
        //Normal and Tangent elastic constants
        //const double sqrt_equiv_radius = sqrt(effective_radius);

        //const double alpha = 0.05;
        const double modified_radius = effective_radius * 0.31225;
        const double mKn_augmenter = 1.0; // 100.0;
        mKn = mKn_augmenter * equiv_young * Globals::Pi * modified_radius; // 2.0 * equiv_young * sqrt_equiv_radius;
        mKt = 4.0 * equiv_shear * mKn / equiv_young;
    }

    void DEM_D_Linear_viscous_Coulomb::CalculateForcesWithFEM(const ProcessInfo& r_process_info,
                                                            const double OldLocalElasticContactForce[3],
                                                            double LocalElasticContactForce[3],
                                                            double LocalDeltDisp[3],
                                                            double LocalRelVel[3],
                                                            double indentation,
                                                            double previous_indentation,
                                                            double ViscoDampingLocalContactForce[3],
                                                            double& cohesive_force,
                                                            SphericParticle* const element,
                                                            Condition* const wall,
                                                            bool& sliding) {

        InitializeContactWithFEM(element, wall, indentation);

        LocalElasticContactForce[2] = CalculateNormalForce(element, wall, indentation);
        cohesive_force              = CalculateCohesiveNormalForceWithFEM(element, wall, indentation);

        CalculateViscoDampingForceWithFEM(LocalRelVel, ViscoDampingLocalContactForce, element, wall);

        double normal_contact_force = LocalElasticContactForce[2] + ViscoDampingLocalContactForce[2];

        if (normal_contact_force < 0.0) {
            normal_contact_force = 0.0;
            ViscoDampingLocalContactForce[2] = -1.0 * LocalElasticContactForce[2];
        }

        double ElasticShearForceModulus;
        double MaximumAdmisibleShearForce;

        CalculateTangentialForceWithNeighbour(normal_contact_force, OldLocalElasticContactForce, LocalElasticContactForce, ViscoDampingLocalContactForce, LocalDeltDisp,
                                              LocalRelVel, sliding, element, wall, indentation, previous_indentation, ElasticShearForceModulus, MaximumAdmisibleShearForce);

        double& elastic_energy = element->GetElasticEnergy();
        CalculateElasticEnergyFEM(elastic_energy, indentation, LocalElasticContactForce);//MSIMSI

        if (ElasticShearForceModulus > MaximumAdmisibleShearForce && MaximumAdmisibleShearForce != 0.0){
            double& inelastic_frictional_energy = element->GetInelasticFrictionalEnergy();
            CalculateInelasticFrictionalEnergyFEM(inelastic_frictional_energy, ElasticShearForceModulus, LocalElasticContactForce);
        }

        double& inelastic_viscodamping_energy = element->GetInelasticViscodampingEnergy();
        CalculateInelasticViscodampingEnergyFEM(inelastic_viscodamping_energy, ViscoDampingLocalContactForce, LocalDeltDisp);
    }

    void DEM_D_Linear_viscous_Coulomb::CalculateViscoDampingForceWithFEM(double LocalRelVel[3],
                                                                         double ViscoDampingLocalContactForce[3],
                                                                         SphericParticle* const element,
                                                                         Condition* const wall) {

        const double my_mass    = element->GetMass();

        Properties& properties_of_this_contact = element->GetProperties().GetSubProperties(wall->GetProperties().Id());
        const double damping_gamma = properties_of_this_contact[DAMPING_GAMMA];

        const double normal_damping_coefficient     = 2.0 * damping_gamma * sqrt(my_mass * mKn);
        const double tangential_damping_coefficient = 2.0 * damping_gamma * sqrt(my_mass * mKt);

        ViscoDampingLocalContactForce[0] = - tangential_damping_coefficient * LocalRelVel[0];
        ViscoDampingLocalContactForce[1] = - tangential_damping_coefficient * LocalRelVel[1];
        ViscoDampingLocalContactForce[2] = - normal_damping_coefficient     * LocalRelVel[2];

    }

    std::size_t DEM_D_Linear_viscous_Coulomb::GetElementId(SphericParticle* element){
        return element->Id();
    }

    double DEM_D_Linear_viscous_Coulomb::CalculateNormalForce(const double indentation) {
        return mKn * indentation;
    }

    double DEM_D_Linear_viscous_Coulomb::CalculateCohesiveNormalForce(SphericParticle* const element1, SphericParticle* const element2, const double indentation){
        return 0.0;
    }

    double DEM_D_Linear_viscous_Coulomb::CalculateCohesiveNormalForceWithFEM(SphericParticle* const element, Condition* const wall, const double indentation){
        return 0.0;
    }

    //MSIMSI
    void DEM_D_Linear_viscous_Coulomb::CalculateElasticEnergyDEM(double& elastic_energy, double indentation, double LocalElasticContactForce[3])
    {
        double normal_elastic         = 0.25*LocalElasticContactForce[2]*indentation; //each ball in a contact with another ball receives half the contact energy
        double tangential_elastic     = 0.25*(LocalElasticContactForce[0]*LocalElasticContactForce[0]+LocalElasticContactForce[1]*LocalElasticContactForce[1])/mKt; //each ball in a contact with another ball receives half the contact energy
        elastic_energy += normal_elastic;
        elastic_energy += tangential_elastic;
    }

    void DEM_D_Linear_viscous_Coulomb::CalculateInelasticFrictionalEnergyDEM(double& inelastic_frictional_energy, double& ElasticShearForceModulus, double LocalElasticContactForce[3])
    {
        double frictional_energy = 0.25*((ElasticShearForceModulus*ElasticShearForceModulus)-(LocalElasticContactForce[0]*LocalElasticContactForce[0]+LocalElasticContactForce[1]*LocalElasticContactForce[1]))/mKt;
        inelastic_frictional_energy += frictional_energy;
    }

    void DEM_D_Linear_viscous_Coulomb::CalculateInelasticViscodampingEnergyDEM(double& inelastic_viscodamping_energy, double ViscoDampingLocalContactForce[3], double LocalDeltDisp[3])
    {
        double viscodamping_energy = 0.50*sqrt(ViscoDampingLocalContactForce[0]*ViscoDampingLocalContactForce[0]*LocalDeltDisp[0]*LocalDeltDisp[0]+ViscoDampingLocalContactForce[1]*ViscoDampingLocalContactForce[1]*LocalDeltDisp[1]*LocalDeltDisp[1]+ViscoDampingLocalContactForce[2]*ViscoDampingLocalContactForce[2]*LocalDeltDisp[2]*LocalDeltDisp[2]);
        inelastic_viscodamping_energy += viscodamping_energy;
    }

    void DEM_D_Linear_viscous_Coulomb::CalculateElasticEnergyFEM(double& elastic_energy, double indentation, double LocalElasticContactForce[3])
    {
        double normal_elastic     = 0.50*LocalElasticContactForce[2]*indentation; //each ball in a contact with a wall receives all the contact energy
        double tangential_elastic = 0.50*(LocalElasticContactForce[0]*LocalElasticContactForce[0]+LocalElasticContactForce[1]*LocalElasticContactForce[1])/mKt;
        elastic_energy += normal_elastic;
        elastic_energy += tangential_elastic;
    }

    void DEM_D_Linear_viscous_Coulomb::CalculateInelasticFrictionalEnergyFEM(double& inelastic_frictional_energy, double& ElasticShearForceModulus, double LocalElasticContactForce[3])
    {
        double frictional_energy = 0.50*((ElasticShearForceModulus*ElasticShearForceModulus)-(LocalElasticContactForce[0]*LocalElasticContactForce[0]+LocalElasticContactForce[1]*LocalElasticContactForce[1]))/mKt;
        inelastic_frictional_energy += frictional_energy;
    }

    void DEM_D_Linear_viscous_Coulomb::CalculateInelasticViscodampingEnergyFEM(double& inelastic_viscodamping_energy, double ViscoDampingLocalContactForce[3], double LocalDeltDisp[3])
    {
        double viscodamping_energy = sqrt(ViscoDampingLocalContactForce[0]*ViscoDampingLocalContactForce[0]*LocalDeltDisp[0]*LocalDeltDisp[0]+ViscoDampingLocalContactForce[1]*ViscoDampingLocalContactForce[1]*LocalDeltDisp[1]*LocalDeltDisp[1]+ViscoDampingLocalContactForce[2]*ViscoDampingLocalContactForce[2]*LocalDeltDisp[2]*LocalDeltDisp[2]);
        inelastic_viscodamping_energy += viscodamping_energy;
    }

} // namespace Kratos
